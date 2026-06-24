/* address: 0x00579a9a */
/* name: CVertexShader__Helper_00579a9a */
/* signature: int CVertexShader__Helper_00579a9a(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CVertexShader__Helper_00579a9a(void)

{
  int iVar1;
  int iVar2;
  void *unaff_EDI;
  uint in_stack_00000014;
  undefined4 *in_stack_00000018;
  void *in_stack_0000001c;
  undefined1 local_114 [128];
  undefined1 local_94 [4];
  undefined1 local_90 [140];

  if (in_stack_00000018 != (undefined4 *)0x0) {
    *in_stack_00000018 = 0;
  }
  CTexture__DirectiveParserContextCtor((int)local_94);
  iVar1 = CTexture__InitializePreprocessorStateFromMemorySpan();
  if (-1 < iVar1) {
    CTexture__ResetParserSemanticValue(local_114);
    iVar1 = CTexture__LoadScriptAndDispatchByVersion
                      (local_114,local_94,in_stack_00000014,0,(int)in_stack_00000018,unaff_EDI);
    CTexture__DestroyParserCompileContext((int)local_114);
    if (-1 < iVar1) {
      iVar2 = CTexture__TokenList_GetCount_0058c378((int)local_90);
      if (iVar2 != 0) {
        iVar1 = -0x7789f4a7;
      }
    }
  }
  if (in_stack_0000001c != (void *)0x0) {
    CTexture__TokenList_EmitConcatenatedText_0058c30f(local_90,in_stack_0000001c,unaff_EDI);
  }
  CTexture__DirectiveParserContextDtor((int)local_94);
  return iVar1;
}
