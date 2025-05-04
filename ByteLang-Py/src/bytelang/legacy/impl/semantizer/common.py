from __future__ import annotations

from typing import final

from bytelang.legacy.abc.profiles import MacroProfile
from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.abc.profiles import TypeProfile
from bytelang.legacy.abc.registry import MutableRegistry
from bytelang.legacy.impl.registry.immediate import MutableImmediateRegistry
from bytelang.legacy.impl.registry.primitive import PrimitiveRegistry
from bytelang.legacy.impl.semantizer.super import SuperSemanticContext


@final
class CommonSemanticContext(SuperSemanticContext[NotImplemented]):
    """Контекст общего назначения"""

    def __init__(self, primitives: PrimitiveRegistry) -> None:
        self._type_registry = self._makeTypeRegistry(primitives)
        """Реестр типов"""

        self._macro_registry = MutableImmediateRegistry[str, MacroProfile](())
        """Реестр макросов"""

        self._const_registry = MutableImmediateRegistry[str, RValueProfile](())
        """Реестр констант"""

    @staticmethod
    def _makeTypeRegistry(primitives: PrimitiveRegistry) -> MutableRegistry[str, TypeProfile]:
        from bytelang.legacy.impl.profiles.type import PrimitiveTypeProfile

        return MutableImmediateRegistry[str, TypeProfile]((
            (key, PrimitiveTypeProfile(item))
            for key, item in primitives.getMappingView().items()
        ))

    def getConstants(self) -> MutableRegistry[str, RValueProfile]:
        return self._const_registry

    def getMacros(self) -> MutableRegistry[str, MacroProfile]:
        return self._macro_registry

    def getTypes(self) -> MutableRegistry[str, TypeProfile]:
        return self._type_registry

    def toBundle(self) -> NotImplemented:
        raise NotImplementedError


def _test():

    from bytelang.legacy.core.lexer import Lexer
    from io import StringIO
    from rustpy.exceptions import Panic
    from bytelang.legacy.core.tokens import TokenType
    from bytelang.legacy.impl.parser.common import CommonParser
    from bytelang.legacy.impl.node.program import Program

    lexer = Lexer(TokenType.build_regex())

    code = """
    .struct vec2 { x: f32, y: f32 }
    .type mat4 = [16]f32
    
    .const c_vec3 = {1, 2, 3} 
    .const c_mat2 = {{1, 2}, {3, 4}}
    
    """

    try:

        tokens = lexer.run(StringIO(code)).unwrap()
        parser = CommonParser(tokens)

        common_semantic_context = CommonSemanticContext(PrimitiveRegistry())

        ast = Program.parse(parser).unwrap()

        ast.accept(common_semantic_context).unwrap()

        print(common_semantic_context.getConstants())

    except Panic as p:
        print(p)

    pass

    pass


if __name__ == '__main__':
    _test()