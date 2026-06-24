/* address: 0x00451a40 */
/* name: CUnitAI__Unk_00451a40 */
/* signature: int * __fastcall CUnitAI__Unk_00451a40(int param_1) */


int * __fastcall CUnitAI__Unk_00451a40(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;

  puVar1 = *(undefined4 **)(param_1 + 0x20);
  *(undefined4 **)(param_1 + 0x28) = puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while( true ) {
    if (piVar2 == (int *)0x0) {
      return (int *)0x0;
    }
    if (DAT_0089d94c == *piVar2) break;
    puVar1 = *(undefined4 **)(*(int *)(param_1 + 0x28) + 4);
    *(undefined4 **)(param_1 + 0x28) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return piVar2;
}
