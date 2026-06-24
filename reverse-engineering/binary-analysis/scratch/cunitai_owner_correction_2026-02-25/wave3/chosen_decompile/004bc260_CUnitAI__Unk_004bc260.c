/* address: 0x004bc260 */
/* name: CUnitAI__Unk_004bc260 */
/* signature: int __thiscall CUnitAI__Unk_004bc260(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CUnitAI__Unk_004bc260(void *this,int param_1,float param_2)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;

  iVar3 = 0;
  DAT_00809598 = 0;
  *(float *)((int)this + 0x2000) = (float)param_1 * _DAT_005dc7b0;
  puVar4 = &DAT_00809dc0;
  for (iVar2 = 0x8000; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar4 = 0xffffffff;
    puVar4 = puVar4 + 1;
  }
  DAT_00829dc4 = 0xff;
  DAT_00829dc8 = 0xff;
  DAT_00630ab4 = 0;
  DAT_00630ab8 = 0;
  do {
    puVar1 = (undefined1 *)(iVar3 + (int)this);
    iVar2 = 0x20;
    do {
      *puVar1 = 0xff;
      puVar1 = puVar1 + 0x100;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    iVar3 = iVar3 + 1;
  } while (iVar3 < 0x100);
  return (int)this;
}
