from collections import deque

from lexer.states import State, SkipState
from parser.fmt import TokenEvent


class ParserInitialState(State):

    # todo enum!
    def on_event(self, event: TokenEvent) -> 'State':
        if event.token.state == 'JavadocState':
            return DeclarationWithDocsState()
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
        elif event.token.state == 'NameState':
            return MethodReturnTypeState()
        elif event.token.state == 'ClosedBracketState':
            return ClosedBracketState()
        elif event.token.state == 'OpenBracketState':
            return OpenBracketState()

        return DeadState()

    @property
    def type(self) -> str:
        return 'InitialState'


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
        elif event.token.state == 'NameState':
            return MethodReturnTypeState()

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
        elif event.token.state == 'NameState':
            return MethodReturnTypeState()

        return DeadState()


class DeclarationWithAccessModifiersState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ModifierState':
            return DeclarationWithModifiersState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'NameState':
            return MethodReturnTypeState()

        return DeadState()


class DeclarationWithModifiersState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ModifierState':
            return self
        elif event.token.state == 'IdentifierState' and event.token.value == 'class':
            return ClassState()
        elif event.token.state == 'IdentifierState' and event.token.value == 'interface':
            return InterfaceState()
        elif event.token.state == 'NameState':
            return MethodReturnTypeState()

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


class MethodReturnTypeState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'NameState':
            return MethodNameState()

        return DeadState()


class MethodNameState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'ArgumentsParenthesisState':
            return MethodArgumentsState()

        return DeadState()


class MethodArgumentsState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ';':
            return SkipState(ParserInitialState(), activate=True, as_state='InterfaceMethodDelimiter')

        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return MethodOpenBracketState()

        return DeadState()


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

    # todo another way

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
        return ParserInitialState().on_event(event)


class OpenBracketState(State):
    separated = True

    def on_event(self, event) -> 'State':
        return ParserInitialState().on_event(event)


class DeadState(State):
    def on_event(self, event):
        return None
