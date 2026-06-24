/* address: 0x00442a80 */
/* name: CDestructableSegment__Unk_00442a80 */
/* signature: void __fastcall CDestructableSegment__Unk_00442a80(int param_1) */


void __fastcall CDestructableSegment__Unk_00442a80(int param_1)

{
  int *piVar1;
  int iVar2;

  *(undefined4 *)(param_1 + 0x1c) = 1;
  piVar1 = *(int **)(param_1 + 0x24);
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while (iVar2 != 0) {
    CDestructableSegment__Unk_00442a80(iVar2);
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  return;
}
