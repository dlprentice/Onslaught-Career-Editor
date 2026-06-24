/* address: 0x00440f80 */
/* name: CDamage__Unk_00440f80 */
/* signature: void __thiscall CDamage__Unk_00440f80(void * this, int param_1, int param_2, int param_3, int param_4) */


void __thiscall CDamage__Unk_00440f80(void *this,int param_1,int param_2,int param_3,int param_4)

{
  ushort *puVar1;
  ushort uVar2;
  ushort uVar3;

  uVar3 = *(ushort *)((int)this + (short)param_1 * 2 + 0x13884);
  if (uVar3 != 0) {
    do {
      puVar1 = (ushort *)((int)this + (uint)uVar3 * 8 + 4);
      if ((*(char *)((int)this + (uint)uVar3 * 8 + 8) == (char)param_2) &&
         (*(char *)((int)puVar1 + 5) == (char)param_3)) {
        uVar3 = *puVar1;
        uVar2 = puVar1[1];
        if ((uVar3 & 0x8000) == 0) {
          *(ushort *)((int)this + (uint)uVar3 * 8 + 6) = uVar2;
        }
        else {
          *(ushort *)((int)this + (uVar3 & 0xffff7fff) * 2 + 0x13884) = uVar2;
        }
        *(ushort *)((int)this + (uint)uVar2 * 8 + 4) = uVar3;
      }
      uVar3 = puVar1[1];
    } while (uVar3 != 0);
  }
  return;
}
