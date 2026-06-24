/* address: 0x004bd440 */
/* name: CEngine__Unk_004bd440 */
/* signature: void __thiscall CEngine__Unk_004bd440(void * this, int param_1, int param_2, int param_3) */


void __thiscall CEngine__Unk_004bd440(void *this,int param_1,int param_2,int param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;

  uVar2 = param_1 + -1 >> 1;
  iVar6 = param_2 >> 1;
  if ((((-1 < (int)uVar2) && ((int)uVar2 < 0x100)) && (-1 < iVar6)) && (iVar6 < 0x100)) {
    pbVar1 = (byte *)((param_1 + -1 >> 4) * 0x100 + iVar6 + (int)this);
    uVar2 = uVar2 & 0x80000007;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xfffffff8) + 1;
    }
    *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar2 & 0x1f)) - 1U;
  }
  uVar2 = param_1 >> 1;
  iVar3 = param_2 + -1 >> 1;
  iVar5 = param_1 >> 4;
  if (-1 < (int)uVar2) {
    if ((((int)uVar2 < 0x100) && (-1 < iVar3)) && (iVar3 < 0x100)) {
      pbVar1 = (byte *)(iVar5 * 0x100 + iVar3 + (int)this);
      uVar4 = uVar2 & 0x80000007;
      if ((int)uVar4 < 0) {
        uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
      }
      *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar4 & 0x1f)) - 1U;
    }
    if (((-1 < (int)uVar2) && ((int)uVar2 < 0x100)) && ((-1 < iVar6 && (iVar6 < 0x100)))) {
      pbVar1 = (byte *)(iVar5 * 0x100 + iVar6 + (int)this);
      uVar4 = uVar2 & 0x80000007;
      if ((int)uVar4 < 0) {
        uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
      }
      *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar4 & 0x1f)) - 1U;
    }
  }
  uVar4 = param_1 + 1 >> 1;
  if ((((-1 < (int)uVar4) && ((int)uVar4 < 0x100)) && (-1 < iVar6)) && (iVar6 < 0x100)) {
    uVar4 = uVar4 & 0x80000007;
    pbVar1 = (byte *)((param_1 + 1 >> 4) * 0x100 + iVar6 + (int)this);
    if ((int)uVar4 < 0) {
      uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
    }
    *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar4 & 0x1f)) - 1U;
  }
  iVar6 = param_2 + 1 >> 1;
  if (((-1 < (int)uVar2) && ((int)uVar2 < 0x100)) && ((-1 < iVar6 && (iVar6 < 0x100)))) {
    pbVar1 = (byte *)(iVar5 * 0x100 + iVar6 + (int)this);
    uVar2 = uVar2 & 0x80000007;
    if ((int)uVar2 < 0) {
      uVar2 = (uVar2 - 1 | 0xfffffff8) + 1;
    }
    *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar2 & 0x1f)) - 1U;
  }
  return;
}
