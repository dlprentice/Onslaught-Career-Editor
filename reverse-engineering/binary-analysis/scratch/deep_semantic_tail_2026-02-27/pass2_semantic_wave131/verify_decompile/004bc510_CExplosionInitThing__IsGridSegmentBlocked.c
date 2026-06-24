/* address: 0x004bc510 */
/* name: CExplosionInitThing__IsGridSegmentBlocked */
/* signature: int __thiscall CExplosionInitThing__IsGridSegmentBlocked(void * this, int param_1, uint param_2, int param_3, uint param_4, float param_5) */


int __thiscall
CExplosionInitThing__IsGridSegmentBlocked
          (void *this,int param_1,uint param_2,int param_3,uint param_4,float param_5)

{
  float fVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint local_c;

  uVar4 = param_2;
  iVar2 = param_1;
  if (((((param_1 < 0) || (0xff < param_1)) || ((int)param_2 < 0)) ||
      ((0xff < (int)param_2 || (param_3 < 0)))) ||
     ((0xff < param_3 || (((int)param_4 < 0 || (0xff < (int)param_4)))))) {
    return 1;
  }
  if (param_3 < param_1) {
    param_1 = param_3;
    param_3 = iVar2;
  }
  uVar6 = param_4;
  if ((int)param_4 < (int)param_2) {
    param_2 = param_4;
    uVar6 = uVar4;
  }
  iVar2 = param_3 - param_1;
  iVar3 = uVar6 - param_2;
  if ((iVar2 != 0) || (iVar3 != 0)) {
    param_4 = 0;
    iVar5 = iVar2;
    if (iVar2 < 0) {
      iVar5 = -iVar2;
    }
    iVar7 = iVar3;
    if (iVar3 < 0) {
      iVar7 = -iVar3;
    }
    if (iVar7 < iVar5) {
      fVar1 = (float)(int)param_2;
      if (iVar2 != 0) {
        param_4 = (uint)((float)iVar3 / (float)iVar2);
      }
      for (; param_1 < param_3 + 1; param_1 = param_1 + 1) {
        local_c = (uint)(longlong)ROUND(fVar1);
        uVar4 = param_1 & 0x80000007;
        if ((int)uVar4 < 0) {
          uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
        }
        if ((*(byte *)((param_1 >> 3) * 0x100 + local_c + (int)this) &
            (byte)(1 << ((byte)uVar4 & 0x1f))) == 0) {
          return 1;
        }
        if ((param_1 == param_3) && (local_c == uVar6)) {
          return 0;
        }
        fVar1 = fVar1 + (float)param_4;
      }
    }
    else {
      fVar1 = (float)param_1;
      if (iVar3 != 0) {
        param_4 = (uint)((float)iVar2 / (float)iVar3);
      }
      if ((int)param_2 < (int)(uVar6 + 1)) {
        while ((local_c = (uint)(longlong)ROUND(fVar1), local_c != param_3 || (param_2 != uVar6))) {
          uVar4 = local_c & 0x80000007;
          if ((int)uVar4 < 0) {
            uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)(((int)local_c >> 3) * 0x100 + param_2 + (int)this) &
              (byte)(1 << ((byte)uVar4 & 0x1f))) == 0) {
            return 1;
          }
          fVar1 = fVar1 + (float)param_4;
          param_2 = param_2 + 1;
          if ((int)(uVar6 + 1) <= (int)param_2) {
            return 0;
          }
        }
      }
    }
  }
  return 0;
}
