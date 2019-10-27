from lexer.states import State, SkipState
from parser.fmt import TokenEvent


class InitialState(State):
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
        return InitialState().on_event(event)


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
            return SkipState(InitialState(), activate=True, skip_count=2, as_state='InterfaceMethodDelimiter')

        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return SkipState(InitialState(), activate=True, skip_count=2, as_state='MethodOpenBracketState')

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
                return SkipState(InitialState(), activate=True, skip_count=2, as_state='InterfaceOpenBracketState')

        return DeadState()


class InterfaceExtendsListState(State):
    def on_event(self, event) -> 'State':
        if event.token.state == 'DelimiterState' and event.token.value == ',':
            if event.lookahead(1)[0].state == 'NameState':
                return SkipState(self)
        elif event.token.state == 'OpenBracketState' and event.token.value == '{':
            return SkipState(InitialState(), activate=True, skip_count=2, as_state='InterfaceOpenBracketState')

        return DeadState()


class DeadState(State):
    def on_event(self, event):
        return None
