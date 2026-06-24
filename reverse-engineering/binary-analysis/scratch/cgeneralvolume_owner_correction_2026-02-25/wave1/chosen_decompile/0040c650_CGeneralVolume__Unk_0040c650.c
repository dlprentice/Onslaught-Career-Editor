/* address: 0x0040c650 */
/* name: CGeneralVolume__Unk_0040c650 */
/* signature: void __fastcall CGeneralVolume__Unk_0040c650(int param_1) */


void __fastcall CGeneralVolume__Unk_0040c650(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;

  iVar2 = CCockpit__Unk_0040f2f0(*(int *)(param_1 + 0x600));
  if (*(int *)(param_1 + 0x4b0) != iVar2) {
    *(int *)(param_1 + 0x4b0) = iVar2;
    *(undefined4 *)(param_1 + 0xfc) = *(undefined4 *)(iVar2 + 0x20);
    *(undefined4 *)(param_1 + 0xf8) = *(undefined4 *)(iVar2 + 0x1c);
    if (*(void **)(param_1 + 0x57c) != (void *)0x0) {
      CSPtrSet_Remove__Wrapper_00412650(*(void **)(param_1 + 0x57c));
    }
    if (*(void **)(param_1 + 0x578) != (void *)0x0) {
      CSPtrSet_Remove__Wrapper_004146b0(*(void **)(param_1 + 0x578));
    }
    puVar3 = (undefined4 *)(param_1 + 0x52c);
    iVar4 = 6;
    do {
      puVar3[6] = 0;
      iVar1 = *(int *)(*(int *)(param_1 + 0x4b0) + (-0x4bc - param_1) + (int)puVar3);
      puVar3[0xc] = iVar1;
      if (iVar1 == 0) {
        *puVar3 = *(undefined4 *)(*(int *)(param_1 + 0x4b0) + (-0x4a4 - param_1) + (int)puVar3);
      }
      else {
        *puVar3 = 0;
      }
      puVar3 = puVar3 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    CConsole__Printf(&DAT_0066f580,*(char **)(iVar2 + 0xa8));
  }
  return;
}
