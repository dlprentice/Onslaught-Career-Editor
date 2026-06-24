/* address: 0x0050d7a0 */
/* name: CWorld__ClearWorldTextSlot */
/* signature: void __thiscall CWorld__ClearWorldTextSlot(void * this, int param_1, int param_2) */


void __thiscall CWorld__ClearWorldTextSlot(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int iVar2;

  puVar1 = (undefined4 *)((int)this + 0x20c);
  iVar2 = 4;
  do {
    if (puVar1[4] == param_1) {
      *puVar1 = 0;
    }
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
