/* address: 0x005b81d0 */
/* name: CTexture__Helper_005b81d0 */
/* signature: void __stdcall CTexture__Helper_005b81d0(void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CTexture__Helper_005b81d0(void *param_1,void *param_2,void *param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  uint uVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  uint uVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  uint uVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  uint uVar26;
  uint uVar27;
  uint uVar28;

  fVar6 = (float)(*(uint *)param_1 & _DAT_0065eb80);
  fVar10 = (float)(*(uint *)((int)param_1 + 4) & uRam0065eb84);
  fVar14 = (float)(*(uint *)((int)param_1 + 8) & uRam0065eb88);
  fVar18 = (float)(*(uint *)((int)param_1 + 0xc) & uRam0065eb8c);
  uVar22 = *(uint *)((int)param_1 + 4) & uRam0065eb74;
  uVar23 = *(uint *)((int)param_1 + 8) & uRam0065eb78;
  uVar24 = *(uint *)((int)param_1 + 0xc) & uRam0065eb7c;
  fVar7 = fVar6 * _DAT_0065eb60 + _DAT_0065eb10;
  fVar11 = fVar10 * fRam0065eb64 + fRam0065eb14;
  fVar15 = fVar14 * fRam0065eb68 + fRam0065eb18;
  fVar19 = fVar18 * fRam0065eb6c + fRam0065eb1c;
  fVar8 = fVar7 - _DAT_0065eb10;
  fVar12 = fVar11 - fRam0065eb14;
  fVar16 = fVar15 - fRam0065eb18;
  fVar20 = fVar19 - fRam0065eb1c;
  fVar6 = (((fVar6 - _DAT_0065eb50 * fVar8) - _DAT_0065eb40 * fVar8) - _DAT_0065eb30 * fVar8) -
          _DAT_0065eb20 * fVar8;
  fVar8 = (((fVar10 - fRam0065eb54 * fVar12) - fRam0065eb44 * fVar12) - fRam0065eb34 * fVar12) -
          fRam0065eb24 * fVar12;
  fVar10 = (((fVar14 - fRam0065eb58 * fVar16) - fRam0065eb48 * fVar16) - fRam0065eb38 * fVar16) -
           fRam0065eb28 * fVar16;
  fVar12 = (((fVar18 - fRam0065eb5c * fVar20) - fRam0065eb4c * fVar20) - fRam0065eb3c * fVar20) -
           fRam0065eb2c * fVar20;
  fVar14 = fVar6 * fVar6;
  fVar16 = fVar8 * fVar8;
  fVar18 = fVar10 * fVar10;
  fVar20 = fVar12 * fVar12;
  uVar25 = (uint)fVar7 & (uint)PTR_DAT_0065eae0;
  uVar26 = (uint)fVar11 & (uint)PTR_DAT_0065eae4;
  uVar27 = (uint)fVar15 & (uint)PTR_DAT_0065eae8;
  uVar28 = (uint)fVar19 & (uint)PTR_DAT_0065eaec;
  uVar9 = uVar25 & _DAT_0065ead0;
  uVar13 = uVar26 & uRam0065ead4;
  uVar17 = uVar27 & uRam0065ead8;
  uVar21 = uVar28 & uRam0065eadc;
  uVar1 = uVar26 - uVar13 & _DAT_0065eac0;
  uVar2 = uVar27 - uVar17 & _DAT_0065eac0;
  uVar3 = uVar28 - uVar21 & _DAT_0065eac0;
  uVar4 = uVar25 + uVar9 & _DAT_0065eac0;
  uVar26 = uVar26 + uVar13 & _DAT_0065eac0;
  uVar27 = uVar27 + uVar17 & _DAT_0065eac0;
  uVar28 = uVar28 + uVar21 & _DAT_0065eac0;
  uVar5 = -(uint)((float)(uVar9 << 0x1e) != 0.0);
  uVar13 = -(uint)((float)(uVar13 << 0x1e) != 0.0);
  uVar17 = -(uint)((float)(uVar17 << 0x1e) != 0.0);
  uVar21 = -(uint)((float)(uVar21 << 0x1e) != 0.0);
  fVar6 = (((_DAT_0065eb00 * fVar14 + _DAT_0065eab0) * fVar14 + _DAT_0065ea90) * fVar14 +
          _DAT_0065ea70) * fVar6;
  fVar8 = (((fRam0065eb04 * fVar16 + fRam0065eab4) * fVar16 + fRam0065ea94) * fVar16 + fRam0065ea74)
          * fVar8;
  fVar10 = (((fRam0065eb08 * fVar18 + fRam0065eab8) * fVar18 + fRam0065ea98) * fVar18 + fRam0065ea78
           ) * fVar10;
  fVar12 = (((fRam0065eb0c * fVar20 + fRam0065eabc) * fVar20 + fRam0065ea9c) * fVar20 + fRam0065ea7c
           ) * fVar12;
  fVar7 = (((_DAT_0065eaf0 * fVar14 + _DAT_0065eaa0) * fVar14 + _DAT_0065ea80) * fVar14 +
          _DAT_0065ea60) * fVar14 + _DAT_0065ea50;
  fVar11 = (((fRam0065eaf4 * fVar16 + fRam0065eaa4) * fVar16 + fRam0065ea84) * fVar16 + fRam0065ea64
           ) * fVar16 + fRam0065ea54;
  fVar14 = (((fRam0065eaf8 * fVar18 + fRam0065eaa8) * fVar18 + fRam0065ea88) * fVar18 + fRam0065ea68
           ) * fVar18 + fRam0065ea58;
  fVar15 = (((fRam0065eafc * fVar20 + fRam0065eaac) * fVar20 + fRam0065ea8c) * fVar20 + fRam0065ea6c
           ) * fVar20 + fRam0065ea5c;
  *(uint *)param_2 =
       (~uVar5 & (uint)fVar6 | uVar5 & (uint)fVar7) ^
       (uVar25 - uVar9 & _DAT_0065eac0) << 0x1e ^ *(uint *)param_1 & _DAT_0065eb70;
  *(uint *)((int)param_2 + 4) =
       (~uVar13 & (uint)fVar8 | uVar13 & (uint)fVar11) ^ uVar1 << 0x1e ^ uVar22;
  *(uint *)((int)param_2 + 8) =
       (~uVar17 & (uint)fVar10 | uVar17 & (uint)fVar14) ^ uVar2 << 0x1e ^ uVar23;
  *(uint *)((int)param_2 + 0xc) =
       (~uVar21 & (uint)fVar12 | uVar21 & (uint)fVar15) ^ uVar3 << 0x1e ^ uVar24;
  *(uint *)param_3 = (uVar5 & (uint)fVar6 | ~uVar5 & (uint)fVar7) ^ uVar4 << 0x1e;
  *(uint *)((int)param_3 + 4) = (uVar13 & (uint)fVar8 | ~uVar13 & (uint)fVar11) ^ uVar26 << 0x1e;
  *(uint *)((int)param_3 + 8) = (uVar17 & (uint)fVar10 | ~uVar17 & (uint)fVar14) ^ uVar27 << 0x1e;
  *(uint *)((int)param_3 + 0xc) = (uVar21 & (uint)fVar12 | ~uVar21 & (uint)fVar15) ^ uVar28 << 0x1e;
  return;
}
