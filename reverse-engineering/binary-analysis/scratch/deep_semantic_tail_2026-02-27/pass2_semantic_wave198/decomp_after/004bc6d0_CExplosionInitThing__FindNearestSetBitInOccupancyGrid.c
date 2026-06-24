/* address: 0x004bc6d0 */
/* name: CExplosionInitThing__FindNearestSetBitInOccupancyGrid */
/* signature: int __thiscall CExplosionInitThing__FindNearestSetBitInOccupancyGrid(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall
CExplosionInitThing__FindNearestSetBitInOccupancyGrid
          (void *this,int param_1,void *param_2,void *param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;

  uVar1 = *(uint *)param_1;
  iVar7 = 0;
  uVar4 = uVar1;
  uVar6 = uVar1;
  uVar5 = uVar1;
  do {
    for (; (int)uVar4 <= (int)uVar5; uVar4 = uVar4 + 1) {
      if ((-1 < (int)uVar4) && ((int)uVar4 < 0x100)) {
        iVar2 = *(int *)param_2;
        if ((-1 < iVar2 - iVar7) && (iVar2 - iVar7 < 0x100)) {
          uVar3 = uVar4 & 0x80000007;
          if ((int)uVar3 < 0) {
            uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)((((int)uVar4 >> 3) * 0x100 - iVar7) + iVar2 + (int)this) &
              (byte)(1 << ((byte)uVar3 & 0x1f))) != 0) {
            *(uint *)param_1 = uVar4;
            *(int *)param_2 = *(int *)param_2 - iVar7;
            return 1;
          }
        }
        if ((-1 < iVar2 + iVar7) && (iVar2 + iVar7 < 0x100)) {
          uVar3 = uVar4 & 0x80000007;
          if ((int)uVar3 < 0) {
            uVar3 = (uVar3 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)(((int)uVar4 >> 3) * 0x100 + iVar2 + iVar7 + (int)this) &
              (byte)(1 << ((byte)uVar3 & 0x1f))) != 0) {
            *(uint *)param_1 = uVar4;
            *(int *)param_2 = *(int *)param_2 + iVar7;
            return 1;
          }
        }
      }
    }
    for (iVar2 = *(int *)param_2 - iVar7; iVar2 <= *(int *)param_2 + iVar7; iVar2 = iVar2 + 1) {
      if ((-1 < iVar2) && (iVar2 < 0x100)) {
        if ((-1 < (int)uVar6) && ((int)uVar6 < 0x100)) {
          uVar4 = uVar6 & 0x80000007;
          if ((int)uVar4 < 0) {
            uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)(((int)uVar6 >> 3) * 0x100 + iVar2 + (int)this) &
              (byte)(1 << ((byte)uVar4 & 0x1f))) != 0) {
            *(uint *)param_1 = uVar1 - iVar7;
            *(int *)param_2 = iVar2;
            return 1;
          }
        }
        if ((-1 < (int)uVar5) && ((int)uVar5 < 0x100)) {
          uVar4 = uVar5 & 0x80000007;
          if ((int)uVar4 < 0) {
            uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)(((int)uVar5 >> 3) * 0x100 + iVar2 + (int)this) &
              (byte)(1 << ((byte)uVar4 & 0x1f))) != 0) {
            *(uint *)param_1 = uVar1 + iVar7;
            *(int *)param_2 = iVar2;
            return 1;
          }
        }
      }
    }
    iVar7 = iVar7 + 1;
    uVar4 = uVar6 - 1;
    uVar5 = uVar5 + 1;
    uVar6 = uVar4;
    if (0xff < iVar7) {
      return 0;
    }
  } while( true );
}
