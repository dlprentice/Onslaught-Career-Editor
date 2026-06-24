/* address: 0x005a1a8e */
/* name: CFastVB__BuildMatrix4x4FromQuaternion */
/* signature: void __stdcall CFastVB__BuildMatrix4x4FromQuaternion(void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__BuildMatrix4x4FromQuaternion(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar17;
  float fVar18;
  undefined1 in_XMM5 [16];
  undefined1 auVar16 [16];
  float fVar19;

  fVar5 = (float)((uint)*(float *)param_3 & _DAT_0065e720);
  fVar8 = (float)((uint)*(float *)((int)param_3 + 4) & uRam0065e724);
  fVar9 = (float)((uint)*(float *)((int)param_3 + 8) & uRam0065e728);
  fVar10 = (float)((uint)*(float *)((int)param_3 + 0xc) & uRam0065e72c);
  fVar6 = fVar5 * fVar5 + fVar9 * fVar9;
  fVar9 = fVar8 * fVar8 + fVar10 * fVar10 + fVar6;
  fVar5 = fVar6;
  fVar8 = fVar6;
  if (fVar9 != 0.0) {
    if ((_DAT_009d3020 & 1) == 0) {
      _DAT_009d3020 = _DAT_009d3020 | 1;
      _DAT_009d3010 = 0.5;
      uRam009d3014 = 0;
      uRam009d3018 = 0;
      uRam009d301c = 0;
    }
    if ((_DAT_009d3020 & 2) == 0) {
      _DAT_009d3020 = _DAT_009d3020 | 2;
      _DAT_009d3000 = 3.0;
      uRam009d3004 = 0;
      uRam009d3008 = 0;
      uRam009d300c = 0;
    }
    auVar16._4_4_ = fVar6;
    auVar16._0_4_ = fVar9;
    auVar16._8_4_ = fVar6;
    auVar16._12_4_ = fVar6;
    auVar16 = rsqrtss(in_XMM5,auVar16);
    fVar5 = auVar16._0_4_;
    fVar8 = _DAT_009d3010 * fVar5 * (_DAT_009d3000 - fVar9 * fVar5 * fVar5);
    fVar9 = *(float *)param_3 * fVar8;
    fVar6 = *(float *)((int)param_3 + 4) * fVar8;
    fVar5 = *(float *)((int)param_3 + 8) * fVar8;
    fVar8 = *(float *)((int)param_3 + 0xc) * fVar8;
  }
  fVar10 = *(float *)param_2;
  fVar1 = *(float *)((int)param_2 + 4);
  fVar2 = *(float *)((int)param_2 + 8);
  fVar3 = *(float *)((int)param_2 + 0xc);
  fVar4 = fVar9 * fVar10 + fVar5 * fVar2 + fVar6 * fVar1 + fVar8 * fVar3;
  fVar9 = (float)((uint)fVar9 ^ _DAT_0065e6e0);
  fVar6 = (float)((uint)fVar6 ^ uRam0065e6e4);
  fVar5 = (float)((uint)fVar5 ^ uRam0065e6e8);
  fVar8 = (float)((uint)fVar8 ^ uRam0065e6ec);
  fVar11 = fVar10 * fVar6 + (float)((uint)fVar4 & _DAT_0065e6f0);
  fVar12 = fVar1 * fVar6 + (float)((uint)fVar4 & uRam0065e6f4);
  fVar13 = fVar2 * fVar6 + (float)((uint)fVar4 & uRam0065e6f8);
  fVar14 = fVar3 * fVar6 + (float)((uint)fVar4 & uRam0065e6fc);
  fVar15 = fVar10 * fVar5 + (float)((uint)fVar4 & _DAT_0065e700);
  fVar17 = fVar1 * fVar5 + (float)((uint)fVar4 & uRam0065e704);
  fVar18 = fVar2 * fVar5 + (float)((uint)fVar4 & uRam0065e708);
  fVar19 = fVar3 * fVar5 + (float)((uint)fVar4 & uRam0065e70c);
  fVar7 = fVar10 * fVar9 + fVar4;
  fVar5 = fVar10 * fVar8 + (float)((uint)fVar4 & _DAT_0065e710);
  fVar6 = fVar1 * fVar8 + (float)((uint)fVar4 & uRam0065e714);
  fVar10 = fVar2 * fVar8 + (float)((uint)fVar4 & uRam0065e718);
  fVar8 = fVar3 * fVar8 + (float)((uint)fVar4 & uRam0065e71c);
  if (((uint)param_1 & 0xf) == 0) {
    *(float *)param_1 = fVar7;
    *(float *)((int)param_1 + 4) = fVar1 * fVar9;
    *(float *)((int)param_1 + 8) = fVar2 * fVar9;
    *(float *)((int)param_1 + 0xc) = fVar3 * fVar9;
    *(float *)((int)param_1 + 0x10) = fVar11;
    *(float *)((int)param_1 + 0x14) = fVar12;
    *(float *)((int)param_1 + 0x18) = fVar13;
    *(float *)((int)param_1 + 0x1c) = fVar14;
    *(float *)((int)param_1 + 0x20) = fVar15;
    *(float *)((int)param_1 + 0x24) = fVar17;
    *(float *)((int)param_1 + 0x28) = fVar18;
    *(float *)((int)param_1 + 0x2c) = fVar19;
    *(float *)((int)param_1 + 0x30) = fVar5;
    *(float *)((int)param_1 + 0x34) = fVar6;
    *(float *)((int)param_1 + 0x38) = fVar10;
    *(float *)((int)param_1 + 0x3c) = fVar8;
  }
  else {
    *(ulonglong *)param_1 = CONCAT44(fVar1 * fVar9,fVar7);
    *(ulonglong *)((int)param_1 + 8) = CONCAT44(fVar3 * fVar9,fVar2 * fVar9);
    *(ulonglong *)((int)param_1 + 0x10) = CONCAT44(fVar12,fVar11);
    *(ulonglong *)((int)param_1 + 0x18) = CONCAT44(fVar14,fVar13);
    *(float *)((int)param_1 + 0x20) = fVar15;
    *(float *)((int)param_1 + 0x24) = fVar17;
    *(float *)((int)param_1 + 0x28) = fVar18;
    *(float *)((int)param_1 + 0x2c) = fVar19;
    *(ulonglong *)((int)param_1 + 0x30) = CONCAT44(fVar6,fVar5);
    *(ulonglong *)((int)param_1 + 0x38) = CONCAT44(fVar8,fVar10);
  }
  return;
}
