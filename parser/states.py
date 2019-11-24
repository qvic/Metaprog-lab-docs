from collections import deque

from lexer.states import State, SkipState
from parser.fmt import TokenEvent


class ParserInitialState(State):

    def on_event(self, event: TokenEvent) -> 'State':
        if event.token.state == 'JavadocState':
            return DeclarationWithDocsState()
        elif event.token.state == 'MultilineCommentState':
            return MultilineCommentState()
        elif event.token.state == 'AnnotationState':
            return DeclarationWithAnnotationsState()
        elif event.token.state == 'AccessModifierState':
            return DeclarationWithAccessModifiersState()
        elif event.token.state == 'ModifierState':
            return DeclarationWithModifiersState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == '@interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'enum':
            return EnumState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'import':
            return ImportState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'package':
            return PackageState()
        elif event.token.state == 'NameState':
            return MethodOrPropertyTypeState()
        elif event.token.state == 'ClosedBracketState':
            return ClosedBracketState()
        elif event.token.state == 'OpenBracketState':
            return OpenBracketState()

        return DeadState()

    @property
    def type(self) -> str:
        return 'InitialState'


class ImportState(State):
    separated = True

    def on_event(self, event) -> 'State':
        lookahead = event.lookahead(2)
        token = event.token

        if token.state == 'ModifierState' and token.value == 'static':
            token = lookahead[0]
            lookahead = lookahead[1]
        else:
            lookahead = lookahead[0]

        if token.state == 'NameState' and lookahead.state == 'DelimiterState' and lookahead.value == ';':
            return SkipState(ParserInitialState(), activate=True, skip_count=2, as_state=self.type)

        return DeadState()


class PackageState(State):

    def on_event(self, event) -> 'State':
        lookahead = event.lookahead(1)[0]
        if event.token.state == 'NameState' and lookahead.state == 'DelimiterState' and lookahead.value == ';':
            return SkipState(ParserInitialState(), activate=True, skip_count=2, as_state=self.type)

        return DeadState()


class DeclarationWithDocsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'AnnotationState':
            return DeclarationWithAnnotationsState()
        elif event.token.state == 'AccessModifierState':
            return DeclarationWithAccessModifiersState()
        elif event.token.state == 'ModifierState':
            return DeclarationWithModifiersState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == '@interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'enum':
            return EnumState()
        elif event.token.state == 'NameState':
            return MethodOrPropertyTypeState()

        return DeadState()


class DeclarationWithAnnotationsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'AnnotationState':
            return self
        elif event.token.state == 'AccessModifierState':
            return DeclarationWithAccessModifiersState()
        elif event.token.state == 'ModifierState':
            return DeclarationWithModifiersState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == '@interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'enum':
            return EnumState()
        elif event.token.state == 'NameState':
            return MethodOrPropertyTypeState()

        return DeadState()


class DeclarationWithAccessModifiersState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ModifierState':
            return DeclarationWithModifiersState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == '@interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'enum':
            return EnumState()
        elif event.token.state == 'NameState':
            return MethodOrPropertyTypeState()

        return DeadState()


class DeclarationWithModifiersState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ModifierState':
            return self
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == '@interface':
            return InterfaceState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'enum':
            return EnumState()
        elif event.token.state == 'NameState':
            return MethodOrPropertyTypeState()

        return DeadState()


class EnumState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return EnumNameState()

        return DeadState()


class EnumNameState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'IdentifierState':
            if event.token.value == 'implements':
                if event.lookahead(1)[0].state == 'NameState':
                    return SkipState(ClassImplementsListState())
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return EnumOpenBracketState()

        return DeadState()


class EnumImplementsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'IdentifierState' and event.token.value == 'implements':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(EnumImplementsListState())
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return EnumOpenBracketState()

        return DeadState()


class EnumImplementsListState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(self)
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return EnumOpenBracketState()

        return DeadState()


class EnumOpenBracketState(State):

    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return EnumValuesListState()

        return DeadState()


class EnumValuesListState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(self)
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return OpenBracketState()
        elif event.token.state == 'DelimiterState' and event.token.value == ';':
            return SkipState(ParserInitialState(), activate=True, as_state='EnumValuesDelimiter')

        return DeadState()


class ClassState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return ClassNameState()

        return DeadState()


class ClassNameState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'IdentifierState':
            if event.token.value == 'extends':
                if event.lookahead(1)[0].state == 'NameState':
                    return SkipState(ClassImplementsState(), activate=True, skip_count=2, as_state='ClassExtendsState')
            elif event.token.value == 'implements':
                if event.lookahead(1)[0].state == 'NameState':
                    return SkipState(ClassImplementsListState())
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return ClassOpenBracketState()

        return DeadState()


class ClassImplementsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'IdentifierState' and event.token.value == 'implements':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(ClassImplementsListState())
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return ClassOpenBracketState()

        return DeadState()


class ClassImplementsListState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(self)
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return ClassOpenBracketState()

        return DeadState()


class ClassOpenBracketState(State):

    def on_event(self, event) -> 'State':
        return ParserInitialState().on_event(event)


class MethodOrPropertyTypeState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return MethodOrPropertyNameState()

        return DeadState()


class MethodOrPropertyNameState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ArgumentsParenthesisState':
            return MethodArgumentsState()
        elif event.token.state == 'DelimiterState':
            if event.token.value in ['=', ';']:
                return SkipState(ParserInitialState(), activate=True, as_state='PropertyDelimiter')

        return DeadState()


class MethodArgumentsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ModifierState':
            if event.token.value in ['throws', 'default']:
                return MethodPostArgumentsState()

        elif event.token.state == 'DelimiterState' and event.token.value == ';':
            return SkipState(ParserInitialState(), activate=True, as_state='InterfaceMethodDelimiter')

        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return MethodOpenBracketState()

        return DeadState()


class MethodPostArgumentsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ';':
            return SkipState(ParserInitialState(), activate=True, as_state='InterfaceMethodDelimiter')

        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return MethodOpenBracketState()

        return self


class InterfaceState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return InterfaceNameState()

        return DeadState()


class InterfaceNameState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'IdentifierState':
            if event.token.value == 'extends':
                if event.lookahead(1)[0].state == 'NameState':
                    return SkipState(InterfaceExtendsListState())
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return SkipState(ParserInitialState(), activate=True, as_state='InterfaceOpenBracketState')

        return DeadState()


class InterfaceExtendsListState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(self)
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return SkipState(ParserInitialState(), activate=True, as_state='InterfaceOpenBracketState')

        return DeadState()


class MethodOpenBracketState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ClosedBracketState':
            return ClosedBracketState()

        return MethodBodyState()


class MethodBodyState(State):

    def __init__(self):
        self.stack = deque()

    def on_event(self, event) -> 'State':
        if event.token.state == 'OpenBracketState':
            self.stack.append('{')
        elif event.token.state == 'ClosedBracketState':
            if len(self.stack) == 0:
                return ClosedBracketState()

            self.stack.pop()

        return self


class ClosedBracketState(State):
    separated = True

    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(EnumValuesListState())
        return ParserInitialState().on_event(event)


class OpenBracketState(State):
    separated = True

    def on_event(self, event) -> 'State':
        return ParserInitialState().on_event(event)


class MultilineCommentState(State):

    def on_event(self, event) -> 'State':
        return ParserInitialState().on_event(event)


class DeadState(State):
    def on_event(self, event):
        return None
