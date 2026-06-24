/* address: 0x004bcbf0 */
/* name: CExplosionInitThing__Unk_004bcbf0 */
/* signature: void CExplosionInitThing__Unk_004bcbf0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CExplosionInitThing__Unk_004bcbf0(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  byte *pbVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int local_8;
  int local_4;

  local_8 = 0;
  local_4 = 0;
  do {
    uVar5 = 0;
    iVar6 = 0;
    do {
      uVar1 = uVar5 & 0x80000007;
      if ((int)uVar1 < 0) {
        uVar1 = (uVar1 - 1 | 0xfffffff8) + 1;
      }
      if (((&DAT_00807580)[local_8 + ((int)uVar5 >> 3) * 0x100] & (byte)(1 << ((byte)uVar1 & 0x1f)))
          == 0) {
        uVar1 = iVar6 >> 1;
        iVar7 = local_4 >> 1;
        if (-1 < (int)uVar1) {
          iVar3 = iVar6 >> 4;
          if ((((int)uVar1 < 0x100) && (-1 < iVar7)) && (iVar7 < 0x100)) {
            pbVar4 = (byte *)(iVar3 * 0x100 + iVar7 + DAT_00855290);
            uVar2 = uVar1 & 0x80000007;
            if ((int)uVar2 < 0) {
              uVar2 = (uVar2 - 1 | 0xfffffff8) + 1;
            }
            *pbVar4 = *pbVar4 & -('\x01' << ((byte)uVar2 & 0x1f)) - 1U;
          }
          if (-1 < (int)uVar1) {
            if ((((int)uVar1 < 0x100) && (-1 < iVar7)) && (iVar7 < 0x100)) {
              pbVar4 = (byte *)(iVar3 * 0x100 + iVar7 + DAT_00855294);
              uVar2 = uVar1 & 0x80000007;
              if ((int)uVar2 < 0) {
                uVar2 = (uVar2 - 1 | 0xfffffff8) + 1;
              }
              *pbVar4 = *pbVar4 & -('\x01' << ((byte)uVar2 & 0x1f)) - 1U;
            }
            if (((-1 < (int)uVar1) && ((int)uVar1 < 0x100)) && ((-1 < iVar7 && (iVar7 < 0x100)))) {
              pbVar4 = (byte *)(iVar3 * 0x100 + iVar7 + DAT_00855298);
              uVar1 = uVar1 & 0x80000007;
              if ((int)uVar1 < 0) {
                uVar1 = (uVar1 - 1 | 0xfffffff8) + 1;
              }
              *pbVar4 = *pbVar4 & -('\x01' << ((byte)uVar1 & 0x1f)) - 1U;
            }
          }
        }
      }
      iVar6 = iVar6 + 2;
      uVar5 = uVar5 + 1;
    } while (iVar6 < 0x200);
    local_4 = local_4 + 2;
    local_8 = local_8 + 1;
  } while (local_4 < 0x200);
  DAT_00809598 = 1;
  return;
}
