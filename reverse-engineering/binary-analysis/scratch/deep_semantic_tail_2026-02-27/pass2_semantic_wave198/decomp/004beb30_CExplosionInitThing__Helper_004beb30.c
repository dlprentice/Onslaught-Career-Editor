/* address: 0x004beb30 */
/* name: CExplosionInitThing__Helper_004beb30 */
/* signature: void CExplosionInitThing__Helper_004beb30(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CExplosionInitThing__Helper_004beb30(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  short *psVar6;
  int iVar7;
  int iVar8;
  int local_1c;
  int local_14;

  local_1c = DAT_00809db4 << 9;
  iVar1 = DAT_00809db4 << 8;
  local_14 = 0;
  iVar4 = DAT_00809db0;
  iVar8 = DAT_00809db4;
  do {
    iVar5 = (DAT_00809db4 - DAT_00809db0) + iVar4;
    iVar7 = iVar8;
    if (iVar8 <= iVar5) {
      psVar6 = (short *)((int)&DAT_00809dc0 + (iVar1 + DAT_00809db0 + local_14) * 2);
      iVar3 = local_1c;
      do {
        if ((-1 < iVar3) && (iVar3 < 0x20000)) {
          iVar2 = (DAT_00809db0 - DAT_00809db4) + iVar8;
          if ((-1 < iVar2) &&
             ((iVar2 < 0x100 &&
              (*(short *)((int)&DAT_00809dc0 + DAT_00809db0 * 2 + iVar3 + local_14 * -2) != -1)))) {
            DAT_00809db4 = iVar7;
            DAT_00809db0 = DAT_00809db0 - local_14;
            return;
          }
          if (((-1 < iVar4) && (iVar4 < 0x100)) && (*psVar6 != -1)) {
            DAT_00809db4 = iVar7;
            DAT_00809db0 = DAT_00809db0 + local_14;
            return;
          }
        }
        iVar7 = iVar7 + 1;
        iVar3 = iVar3 + 0x200;
        psVar6 = psVar6 + 0x100;
      } while (iVar7 <= iVar5);
    }
    for (iVar3 = (DAT_00809db0 - DAT_00809db4) + iVar8; iVar3 <= iVar4; iVar3 = iVar3 + 1) {
      if ((-1 < iVar3) && (iVar3 < 0x100)) {
        if ((-1 < iVar8) &&
           ((iVar8 < 0x100 && (*(short *)((int)&DAT_00809dc0 + (iVar1 + iVar3) * 2) != -1)))) {
          DAT_00809db0 = iVar3;
          DAT_00809db4 = DAT_00809db4 - local_14;
          return;
        }
        if (((-1 < iVar5) && (iVar5 < 0x100)) &&
           (*(short *)((int)&DAT_00809dc0 + ((DAT_00809db4 + iVar7) * 0x100 + iVar3) * 2) != -1)) {
          DAT_00809db0 = iVar3;
          DAT_00809db4 = DAT_00809db4 + local_14;
          return;
        }
      }
    }
    local_14 = local_14 + 1;
    iVar1 = iVar1 + -0x100;
    iVar8 = iVar8 + -1;
    local_1c = local_1c + -0x200;
    iVar4 = iVar4 + 1;
    if (0xff < local_14) {
      return;
    }
  } while( true );
}
