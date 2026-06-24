/* address: 0x004c7db0 */
/* name: CExplosionInitThing__Unk_004c7db0 */
/* signature: void CExplosionInitThing__Unk_004c7db0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CExplosionInitThing__Unk_004c7db0(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  undefined4 *puVar12;
  int iVar13;
  uint local_24;
  float local_20;

  if (DAT_0082b398 == '\0') {
    DAT_0082b398 = '\x01';
    puVar12 = &DAT_0082a358;
    for (iVar8 = 0x400; iVar8 != 0; iVar8 = iVar8 + -1) {
      *puVar12 = 0;
      puVar12 = puVar12 + 1;
    }
    local_24 = 0x20;
    do {
      uVar2 = local_24 >> 1;
      iVar8 = uVar2 * 0x50;
      uVar11 = 0;
      do {
        uVar9 = local_24 + uVar11;
        iVar13 = (uVar9 & 0x1f) * 0x20;
        iVar3 = (uVar2 + uVar11 & 0x1f) * 0x20;
        iVar10 = (uVar11 & 0x1f) * 0x20;
        uVar11 = 0;
        do {
          iVar4 = _rand();
          uVar5 = uVar11 & 0x1f;
          iVar7 = uVar5 + iVar13;
          iVar1 = iVar10 + uVar5;
          (&DAT_0082a358)[iVar3 + uVar5] =
               (float)((iVar4 / 3 + -0x1000) * iVar8 >> 0xc) * _DAT_005ddba8 +
               ((float)(&DAT_0082a358)[iVar7] + (float)(&DAT_0082a358)[iVar1]) * _DAT_005d85ec;
          iVar6 = _rand();
          uVar5 = local_24 + uVar11;
          iVar4 = (uVar5 & 0x1f) + iVar10;
          uVar11 = uVar11 + uVar2 & 0x1f;
          (&DAT_0082a358)[uVar11 + iVar3] =
               (float)((iVar6 / 3 + -0x1000) * iVar8 >> 0xc) * _DAT_005ddba8 +
               ((float)(&DAT_0082a358)[(uVar5 & 0x1f) + iVar13] + (float)(&DAT_0082a358)[iVar4] +
                (float)(&DAT_0082a358)[iVar7] + (float)(&DAT_0082a358)[iVar1]) * _DAT_005d858c;
          iVar7 = _rand();
          (&DAT_0082a358)[uVar11 + iVar10] =
               (float)((iVar7 / 3 + -0x1000) * iVar8 >> 0xc) * _DAT_005ddba8 +
               ((float)(&DAT_0082a358)[iVar4] + (float)(&DAT_0082a358)[iVar1]) * _DAT_005d85ec;
          uVar11 = uVar5;
        } while ((int)uVar5 < 0x20);
        uVar11 = uVar9;
      } while ((int)uVar9 < 0x20);
      local_24 = (int)local_24 >> 1;
    } while (1 < local_24);
    local_20 = 0.0;
    uVar11 = 0;
    do {
      uVar2 = 0;
      do {
        if (local_20 < ABS((float)(&DAT_0082a358)[(uVar2 & 0x1f) + (uVar11 & 0x1f) * 0x20])) {
          local_20 = ABS((float)(&DAT_0082a358)[(uVar2 & 0x1f) + (uVar11 & 0x1f) * 0x20]);
        }
        uVar2 = uVar2 + local_24;
      } while ((int)uVar2 < 0x20);
      uVar11 = uVar11 + local_24;
    } while ((int)uVar11 < 0x20);
    if (_DAT_005d856c < local_20) {
      local_20 = _DAT_005d8568 / local_20;
      uVar11 = 0;
      do {
        uVar2 = 0;
        do {
          uVar9 = uVar2 & 0x1f;
          uVar2 = uVar2 + local_24;
          iVar8 = uVar9 + (uVar11 & 0x1f) * 0x20;
          (&DAT_0082a358)[iVar8] = local_20 * (float)(&DAT_0082a358)[iVar8];
        } while ((int)uVar2 < 0x20);
        uVar11 = uVar11 + local_24;
      } while ((int)uVar11 < 0x20);
    }
  }
  return;
}
