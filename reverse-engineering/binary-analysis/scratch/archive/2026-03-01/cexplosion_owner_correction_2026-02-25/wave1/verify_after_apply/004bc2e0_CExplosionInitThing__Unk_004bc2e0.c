/* address: 0x004bc2e0 */
/* name: CExplosionInitThing__Unk_004bc2e0 */
/* signature: int CExplosionInitThing__Unk_004bc2e0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CExplosionInitThing__Unk_004bc2e0(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;

  iVar6 = DAT_00829dc4 + -1;
  iVar2 = DAT_00829dc8 + -1;
  iVar5 = DAT_00630ab4 + 1;
  iVar1 = DAT_00630ab8 + 1;
  if (iVar6 < 0) {
    iVar6 = 0;
  }
  if (iVar2 < 0) {
    iVar2 = 0;
  }
  if (0x100 < iVar5) {
    iVar5 = 0x100;
  }
  if (0x100 < iVar1) {
    iVar1 = 0x100;
  }
  if (iVar2 < iVar1) {
    iVar4 = iVar2 << 8;
    iVar1 = iVar1 - iVar2;
    do {
      if (iVar6 < iVar5) {
        puVar7 = (undefined4 *)((int)&DAT_00809dc0 + (iVar4 + iVar6) * 2);
        for (uVar3 = (uint)(iVar5 - iVar6) >> 1; uVar3 != 0; uVar3 = uVar3 - 1) {
          *puVar7 = 0xffffffff;
          puVar7 = puVar7 + 1;
        }
        for (uVar3 = (uint)((iVar5 - iVar6 & 1U) != 0); uVar3 != 0; uVar3 = uVar3 - 1) {
          *(undefined2 *)puVar7 = 0xffff;
          puVar7 = (undefined4 *)((int)puVar7 + 2);
        }
      }
      iVar4 = iVar4 + 0x100;
      iVar1 = iVar1 + -1;
    } while (iVar1 != 0);
  }
  DAT_00829dc4 = 0xff;
  DAT_00829dc8 = 0xff;
  DAT_00630ab4 = 0;
  DAT_00630ab8 = 0;
  iVar1 = CExplosionInitThing__Unk_004be1d0();
  return iVar1;
}
