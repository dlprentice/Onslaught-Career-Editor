/* address: 0x004bdf70 */
/* name: CWorld__Helper_004bdf70 */
/* signature: void __thiscall CWorld__Helper_004bdf70(void * this, int param_1, int param_2, int param_3, int param_4) */


void __thiscall CWorld__Helper_004bdf70(void *this,int param_1,int param_2,int param_3,int param_4)

{
  byte *pbVar1;
  int iVar2;
  uint uVar3;

  uVar3 = param_1 >> 1;
  iVar2 = param_2 >> 1;
  if ((((-1 < (int)uVar3) && ((int)uVar3 < 0x100)) && (-1 < iVar2)) && (iVar2 < 0x100)) {
    if (param_3 != 0) {
      uVar3 = uVar3 & 0x80000007;
      pbVar1 = (byte *)((param_1 >> 4) * 0x100 + iVar2 + (int)this);
      if ((int)uVar3 < 0) {
        uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
      }
      *pbVar1 = *pbVar1 | '\x01' << ((byte)uVar3 & 0x1f);
      return;
    }
    uVar3 = uVar3 & 0x80000007;
    pbVar1 = (byte *)((param_1 >> 4) * 0x100 + iVar2 + (int)this);
    if ((int)uVar3 < 0) {
      uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
    }
    *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar3 & 0x1f)) - 1U;
  }
  return;
}
