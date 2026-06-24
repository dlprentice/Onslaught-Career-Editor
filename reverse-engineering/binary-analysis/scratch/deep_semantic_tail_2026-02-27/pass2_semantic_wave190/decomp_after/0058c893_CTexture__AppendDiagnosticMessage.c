/* address: 0x0058c893 */
/* name: CTexture__AppendDiagnosticMessage */
/* signature: void __cdecl CTexture__AppendDiagnosticMessage(void * param_1, int param_2, int param_3, int param_4) */


void __cdecl CTexture__AppendDiagnosticMessage(void *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined1 *puVar2;
  void *unaff_EDI;
  int iVar3;
  undefined1 local_1004 [4064];
  undefined4 uStackY_24;

  CRT__AllocaProbe();
  puVar2 = local_1004;
  iVar3 = 0xffe;
  if (param_2 != 0) {
    if (*(int *)(param_2 + 0x10) != 0) {
      uStackY_24 = 0x58c8cf;
      iVar3 = CTexture__Helper_005d075f(local_1004,0xffe,&DAT_005ea38c);
      if (iVar3 < 0) {
        iVar3 = 0xffe;
      }
      puVar2 = local_1004 + iVar3;
      iVar3 = 0xffe - iVar3;
    }
    uStackY_24 = 0x58c8f6;
    iVar1 = CTexture__Helper_005d075f(puVar2,iVar3,"(%u): ");
    if (iVar1 < 0) {
      iVar1 = iVar3;
    }
    puVar2 = puVar2 + iVar1;
    iVar3 = iVar3 - iVar1;
  }
  if (param_3 != 0) {
    uStackY_24 = 0x58c918;
    iVar1 = CTexture__Helper_005d075f(puVar2,iVar3,"error X%u: ");
    if (iVar1 < 0) {
      iVar1 = iVar3;
    }
    puVar2 = puVar2 + iVar1;
    iVar3 = iVar3 - iVar1;
  }
  uStackY_24 = 0x58c933;
  iVar1 = CRT__VsnprintfAndTerminate_005d070f(puVar2,iVar3,(void *)param_4,&stack0x00000014);
  if (iVar1 < 0) {
    iVar1 = iVar3;
  }
  (puVar2 + iVar1)[1] = 0;
  puVar2[iVar1] = 10;
  *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
  CTexture__AppendDiagnosticTextLine(param_1,local_1004,unaff_EDI);
  return;
}
