/* address: 0x005b83b9 */
/* name: CDXTexture__Helper_005b83b9 */
/* signature: void __stdcall CDXTexture__Helper_005b83b9(void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CDXTexture__Helper_005b83b9(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  uint uVar3;
  float fVar4;
  float fVar5;
  uint uVar6;
  float fVar7;
  float fVar8;
  uint uVar9;
  float fVar10;
  float fVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  float fVar16;
  float fVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  float fVar25;
  float fVar26;
  uint uVar27;
  uint uVar28;

  fVar16 = (float)(*(uint *)param_1 & _DAT_0065ecc0);
  fVar17 = (float)(*(uint *)((int)param_1 + 4) & uRam0065ecc4);
  fVar25 = (float)(*(uint *)((int)param_1 + 8) & uRam0065ecc8);
  fVar26 = (float)(*(uint *)((int)param_1 + 0xc) & uRam0065eccc);
  uVar13 = *(uint *)((int)param_1 + 4) & uRam0065ecb4;
  uVar14 = *(uint *)((int)param_1 + 8) & uRam0065ecb8;
  uVar15 = *(uint *)((int)param_1 + 0xc) & uRam0065ecbc;
  fVar1 = fVar16 * _DAT_0065eca0 + _DAT_0065ec50;
  fVar4 = fVar17 * fRam0065eca4 + fRam0065ec54;
  fVar7 = fVar25 * fRam0065eca8 + fRam0065ec58;
  fVar10 = fVar26 * fRam0065ecac + fRam0065ec5c;
  fVar2 = fVar1 - _DAT_0065ec50;
  fVar5 = fVar4 - fRam0065ec54;
  fVar8 = fVar7 - fRam0065ec58;
  fVar11 = fVar10 - fRam0065ec5c;
  fVar16 = (((fVar16 - _DAT_0065ec90 * fVar2) - _DAT_0065ec80 * fVar2) - _DAT_0065ec70 * fVar2) -
           _DAT_0065ec60 * fVar2;
  fVar2 = (((fVar17 - fRam0065ec94 * fVar5) - fRam0065ec84 * fVar5) - fRam0065ec74 * fVar5) -
          fRam0065ec64 * fVar5;
  fVar17 = (((fVar25 - fRam0065ec98 * fVar8) - fRam0065ec88 * fVar8) - fRam0065ec78 * fVar8) -
           fRam0065ec68 * fVar8;
  fVar5 = (((fVar26 - fRam0065ec9c * fVar11) - fRam0065ec8c * fVar11) - fRam0065ec7c * fVar11) -
          fRam0065ec6c * fVar11;
  fVar25 = fVar16 * fVar16;
  fVar8 = fVar2 * fVar2;
  fVar26 = fVar17 * fVar17;
  fVar11 = fVar5 * fVar5;
  uVar18 = (uint)fVar1 & (uint)PTR_DAT_0065ec20;
  uVar19 = (uint)fVar4 & (uint)PTR_DAT_0065ec24;
  uVar21 = (uint)fVar7 & (uint)PTR_DAT_0065ec28;
  uVar23 = (uint)fVar10 & (uint)PTR_DAT_0065ec2c;
  uVar3 = uVar18 & _DAT_0065ec10;
  uVar6 = uVar19 & uRam0065ec14;
  uVar9 = uVar21 & uRam0065ec18;
  uVar12 = uVar23 & uRam0065ec1c;
  uVar20 = uVar19 - uVar6 & uRam0065ec04;
  uVar22 = uVar21 - uVar9 & uRam0065ec08;
  uVar24 = uVar23 - uVar12 & uRam0065ec0c;
  uVar27 = uVar18 + uVar3 & _DAT_0065ec00;
  uVar28 = uVar19 + uVar6 & uRam0065ec04;
  uVar21 = uVar21 + uVar9 & uRam0065ec08;
  uVar23 = uVar23 + uVar12 & uRam0065ec0c;
  uVar19 = -(uint)((float)(uVar3 << 0x1e) != 0.0);
  uVar6 = -(uint)((float)(uVar6 << 0x1e) != 0.0);
  uVar9 = -(uint)((float)(uVar9 << 0x1e) != 0.0);
  uVar12 = -(uint)((float)(uVar12 << 0x1e) != 0.0);
  fVar16 = (((_DAT_0065ec40 * fVar25 + _DAT_0065ebf0) * fVar25 + _DAT_0065ebd0) * fVar25 +
           _DAT_0065ebb0) * fVar16;
  fVar2 = (((fRam0065ec44 * fVar8 + fRam0065ebf4) * fVar8 + fRam0065ebd4) * fVar8 + fRam0065ebb4) *
          fVar2;
  fVar17 = (((fRam0065ec48 * fVar26 + fRam0065ebf8) * fVar26 + fRam0065ebd8) * fVar26 + fRam0065ebb8
           ) * fVar17;
  fVar5 = (((fRam0065ec4c * fVar11 + fRam0065ebfc) * fVar11 + fRam0065ebdc) * fVar11 + fRam0065ebbc)
          * fVar5;
  fVar1 = (((_DAT_0065ec30 * fVar25 + _DAT_0065ebe0) * fVar25 + _DAT_0065ebc0) * fVar25 +
          _DAT_0065eba0) * fVar25 + _DAT_0065eb90;
  fVar4 = (((fRam0065ec34 * fVar8 + fRam0065ebe4) * fVar8 + fRam0065ebc4) * fVar8 + fRam0065eba4) *
          fVar8 + fRam0065eb94;
  fVar25 = (((fRam0065ec38 * fVar26 + fRam0065ebe8) * fVar26 + fRam0065ebc8) * fVar26 + fRam0065eba8
           ) * fVar26 + fRam0065eb98;
  fVar7 = (((fRam0065ec3c * fVar11 + fRam0065ebec) * fVar11 + fRam0065ebcc) * fVar11 + fRam0065ebac)
          * fVar11 + fRam0065eb9c;
  *(uint *)param_2 =
       (~uVar19 & (uint)fVar16 | uVar19 & (uint)fVar1) ^
       (uVar18 - uVar3 & _DAT_0065ec00) << 0x1e ^ *(uint *)param_1 & _DAT_0065ecb0;
  *(uint *)((int)param_2 + 4) =
       (~uVar6 & (uint)fVar2 | uVar6 & (uint)fVar4) ^ uVar20 << 0x1e ^ uVar13;
  *(uint *)((int)param_2 + 8) =
       (~uVar9 & (uint)fVar17 | uVar9 & (uint)fVar25) ^ uVar22 << 0x1e ^ uVar14;
  *(uint *)((int)param_2 + 0xc) =
       (~uVar12 & (uint)fVar5 | uVar12 & (uint)fVar7) ^ uVar24 << 0x1e ^ uVar15;
  *(uint *)param_3 = (uVar19 & (uint)fVar16 | ~uVar19 & (uint)fVar1) ^ uVar27 << 0x1e;
  *(uint *)((int)param_3 + 4) = (uVar6 & (uint)fVar2 | ~uVar6 & (uint)fVar4) ^ uVar28 << 0x1e;
  *(uint *)((int)param_3 + 8) = (uVar9 & (uint)fVar17 | ~uVar9 & (uint)fVar25) ^ uVar21 << 0x1e;
  *(uint *)((int)param_3 + 0xc) = (uVar12 & (uint)fVar5 | ~uVar12 & (uint)fVar7) ^ uVar23 << 0x1e;
  return;
}
