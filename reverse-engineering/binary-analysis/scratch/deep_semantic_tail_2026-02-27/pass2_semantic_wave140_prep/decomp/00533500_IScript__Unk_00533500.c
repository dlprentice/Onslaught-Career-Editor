/* address: 0x00533500 */
/* name: IScript__Unk_00533500 */
/* signature: void __fastcall IScript__Unk_00533500(int param_1) */


void __fastcall IScript__Unk_00533500(int param_1)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;

  if (DAT_008a9ac0 == 4) {
    CScriptObjectCode__Reset();
  }
  else {
    CScriptObjectCode__CallEvent(*(undefined4 *)(param_1 + 0xc),0,0,0);
  }
  iVar1 = *(int *)(param_1 + 0xc);
  piVar2 = *(int **)(iVar1 + 0x48);
  *(int **)(iVar1 + 0x50) = piVar2;
  if (piVar2 == (int *)0x0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *piVar2;
  }
  while (iVar4 != 0) {
    piVar2 = *(int **)(iVar4 + 0xc);
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
    while (iVar5 != 0) {
      uVar3 = CScriptEventNB__RegisterEventListener(iVar5,iVar4);
      *(undefined4 *)(iVar5 + 4) = uVar3;
      piVar2 = (int *)piVar2[1];
      if (piVar2 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piVar2;
      }
    }
    piVar2 = *(int **)(*(int *)(iVar1 + 0x50) + 4);
    *(int **)(iVar1 + 0x50) = piVar2;
    if (piVar2 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar2;
    }
  }
  return;
}
