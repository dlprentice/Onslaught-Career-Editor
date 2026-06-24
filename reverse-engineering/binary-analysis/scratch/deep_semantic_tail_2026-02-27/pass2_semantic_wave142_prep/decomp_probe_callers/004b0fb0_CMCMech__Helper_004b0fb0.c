/* address: 0x004b0fb0 */
/* name: CMCMech__Helper_004b0fb0 */
/* signature: int CMCMech__Helper_004b0fb0(void) */


/* WARNING: Type propagation algorithm not settling */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMCMech__Helper_004b0fb0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  float *pfVar5;
  void *extraout_EAX;
  float extraout_EAX_00;
  void *extraout_EAX_01;
  undefined4 *puVar6;
  int *piVar7;
  float *extraout_EAX_02;
  float *extraout_EAX_03;
  float *extraout_EAX_04;
  int in_ECX;
  int iVar8;
  float *pfVar9;
  char cVar10;
  void *this;
  void *unaff_EDI;
  int iVar11;
  void *pvVar12;
  int in_stack_00000004;
  int in_stack_00000008;
  undefined4 *in_stack_0000000c;
  int *in_stack_00000010;
  float *in_stack_00000014;
  float *in_stack_00000018;
  undefined4 in_stack_0000001c;
  char in_stack_00000020;
  char in_stack_00000024;
  float fStack_16c;
  float fStack_168;
  float fStack_164;
  float fStack_160;
  int iStack_15c;
  float local_158;
  float fStack_154;
  float fStack_150;
  float fStack_14c;
  float fStack_148;
  float fStack_144;
  float fStack_140;
  float fStack_138;
  float fStack_134;
  float fStack_130;
  float fStack_128;
  float fStack_124;
  float fStack_120;
  int local_114;
  float fStack_110;
  float fStack_10c;
  float fStack_108;
  float fStack_104;
  float fStack_100;
  float fStack_fc;
  float fStack_f8;
  undefined1 auStack_f4 [4];
  undefined1 auStack_f0 [16];
  float afStack_e0 [4];
  undefined4 uStack_d0;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_c4;
  undefined4 uStack_c0;
  undefined4 uStack_bc;
  undefined4 uStack_b8;
  float afStack_b4 [13];
  undefined1 auStack_80 [16];
  undefined1 auStack_70 [32];
  undefined1 auStack_50 [16];
  undefined1 auStack_40 [16];
  undefined1 auStack_30 [16];
  undefined1 auStack_20 [16];
  undefined1 auStack_10 [16];

  fVar4 = DAT_008a9aac;
  local_158 = DAT_008a9aac;
  local_114 = in_ECX;
  if ((in_stack_00000010 == (int *)0x0) || (in_stack_00000020 == '\0')) {
    iVar3 = 0;
  }
  else {
    iVar3 = (**(code **)(*in_stack_00000010 + 0x70))();
  }
  cVar10 = (char)in_stack_0000001c;
  if ((((in_stack_00000010 != (int *)0x0) && (in_stack_00000010 == DAT_00704da0)) &&
      (DAT_00704da4 == in_ECX)) && (iVar3 == 0)) {
    if (cVar10 == '\0') {
      if ((fVar4 == DAT_00704d5c) && (in_stack_00000004 == DAT_00704d54)) {
        pfVar5 = (float *)&DAT_00704d20;
        for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
          *in_stack_00000014 = *pfVar5;
          pfVar5 = pfVar5 + 1;
          in_stack_00000014 = in_stack_00000014 + 1;
        }
        *in_stack_00000018 = DAT_00704ce0;
        in_stack_00000018[1] = DAT_00704ce4;
        in_stack_00000018[2] = DAT_00704ce8;
        fVar4 = DAT_00704cec;
        in_stack_00000018[3] = DAT_00704cec;
        return (int)fVar4;
      }
    }
    else if (((cVar10 == '\x01') && (fVar4 == DAT_00704d58)) && (in_stack_00000004 == DAT_00704d50))
    {
      pfVar5 = (float *)&DAT_00704cf0;
      for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
        *in_stack_00000014 = *pfVar5;
        pfVar5 = pfVar5 + 1;
        in_stack_00000014 = in_stack_00000014 + 1;
      }
      *in_stack_00000018 = DAT_00704cd0;
      in_stack_00000018[1] = DAT_00704cd4;
      fVar4 = DAT_00704cd8;
      in_stack_00000018[2] = DAT_00704cd8;
      in_stack_00000018[3] = DAT_00704cdc;
      return (int)fVar4;
    }
  }
  if (((iVar3 == 0) && (in_stack_00000024 == '\0')) && (0 < *(int *)(in_ECX + 0x118))) {
    iVar3 = *(int *)(in_ECX + 0x11c);
    iVar1 = in_ECX;
    while (iVar3 != 0) {
      iVar1 = *(int *)(iVar1 + 0x98);
      iVar3 = *(int *)(iVar1 + 0x11c);
    }
    iVar3 = *(int *)(in_ECX + 0x120);
    iStack_15c = in_ECX;
    while (iVar3 != 0) {
      iStack_15c = *(int *)(iStack_15c + 0x98);
      iVar3 = *(int *)(iStack_15c + 0x120);
    }
    iVar11 = *(int *)(iVar1 + 0x118);
    iVar3 = in_stack_00000004;
    if (iVar11 <= in_stack_00000004) {
      iVar3 = iVar11 + -1;
    }
    iVar8 = in_stack_00000008;
    if (iVar11 <= in_stack_00000008) {
      iVar8 = iVar11 + -1;
    }
    iVar2 = *(int *)(iStack_15c + 0x118);
    iVar11 = in_stack_00000004;
    if (iVar2 <= in_stack_00000004) {
      iVar11 = iVar2 + -1;
    }
    if (iVar2 <= in_stack_00000008) {
      in_stack_00000008 = iVar2 + -1;
    }
    iVar1 = *(int *)(iVar1 + 0x104);
    pfVar9 = (float *)(iVar8 * 0x10 + iVar1);
    iVar3 = iVar3 * 0x10;
    fStack_10c = pfVar9[1] - *(float *)(iVar3 + 4 + iVar1);
    pfVar5 = (float *)(iVar3 + iVar1);
    fStack_108 = pfVar9[2] - pfVar5[2];
    fStack_fc = fStack_10c * (float)in_stack_0000000c;
    fStack_f8 = fStack_108 * (float)in_stack_0000000c;
    fStack_154 = (*pfVar9 - *(float *)(iVar3 + iVar1)) * (float)in_stack_0000000c + *pfVar5;
    fStack_150 = fStack_fc + pfVar5[1];
    fStack_14c = fStack_f8 + pfVar5[2];
    *in_stack_00000018 = fStack_154;
    in_stack_00000018[1] = fStack_150;
    in_stack_00000018[2] = fStack_14c;
    in_stack_00000018[3] = fStack_148;
    this = (void *)(in_stack_00000008 * 0x30 + *(int *)(iStack_15c + 0x108));
    pvVar12 = (void *)(iVar11 * 0x30 + *(int *)(iStack_15c + 0x108));
    Vec3__SetXYZ();
    CMeshCollisionVolume__Helper_0040d120
              ((void *)((int)this + 0x10),auStack_20,(void *)((int)pvVar12 + 0x10),&fStack_100);
    CMeshCollisionVolume__Helper_0040d120(this,auStack_40,pvVar12,extraout_EAX);
    Mat34__SetRows();
    Vec3__SetXYZ();
    CExplosionInitThing__Helper_0040d150
              (&fStack_134,auStack_30,in_stack_0000000c,(float)&fStack_110);
    CExplosionInitThing__Helper_0040d150(&fStack_144,auStack_10,in_stack_0000000c,extraout_EAX_00);
    Mat34__SetRows();
    pvVar12 = (void *)(iVar11 * 0x30 + *(int *)(iStack_15c + 0x108));
    Vec3__SetXYZ();
    Vec3__Add((void *)((int)pvVar12 + 0x10),auStack_50,auStack_70,&fStack_154);
    Vec3__Add(pvVar12,auStack_f0,auStack_80,extraout_EAX_01);
    Mat34__SetRows();
    pfVar5 = afStack_b4;
    pfVar9 = in_stack_00000014;
    for (iVar3 = 0xc; pfVar5 = (float *)((int)pfVar5 + 4), iVar3 != 0; iVar3 = iVar3 + -1) {
      *pfVar9 = *pfVar5;
      pfVar9 = pfVar9 + 1;
    }
    if (cVar10 != '\0') {
      pfVar5 = afStack_b4;
      pfVar9 = (float *)&DAT_00704cf0;
      for (iVar3 = 0xc; pfVar5 = (float *)((int)pfVar5 + 4), iVar3 != 0; iVar3 = iVar3 + -1) {
        *pfVar9 = *pfVar5;
        pfVar9 = pfVar9 + 1;
      }
      DAT_00704cd0 = *in_stack_00000018;
      DAT_00704cd4 = in_stack_00000018[1];
      DAT_00704cd8 = in_stack_00000018[2];
      DAT_00704cdc = in_stack_00000018[3];
      DAT_00704d50 = in_stack_00000004;
      DAT_00704d58 = local_158;
      DAT_00704da4 = local_114;
      DAT_00704da0 = in_stack_00000010;
      return (int)in_stack_00000010;
    }
    if (in_stack_00000010 != (int *)0x0) {
      (**(code **)(*in_stack_00000010 + 4))(&fStack_144);
      fStack_104 = fStack_124 * in_stack_00000014[4] +
                   fStack_120 * in_stack_00000014[8] + fStack_128 * *in_stack_00000014;
      fStack_100 = fStack_120 * in_stack_00000014[9] +
                   fStack_124 * in_stack_00000014[5] + fStack_128 * in_stack_00000014[1];
      fStack_fc = fStack_124 * in_stack_00000014[6] +
                  fStack_128 * in_stack_00000014[2] + fStack_120 * in_stack_00000014[10];
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Mat34__SetRows();
      pfVar5 = afStack_b4;
      pfVar9 = in_stack_00000014;
      for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
        *pfVar9 = *pfVar5;
        pfVar5 = pfVar5 + 1;
        pfVar9 = pfVar9 + 1;
      }
      local_158 = fStack_148 * *in_stack_00000018 +
                  fStack_144 * in_stack_00000018[1] + fStack_140 * in_stack_00000018[2];
      fStack_154 = fStack_138 * *in_stack_00000018 +
                   fStack_134 * in_stack_00000018[1] + fStack_130 * in_stack_00000018[2];
      fStack_150 = fStack_128 * *in_stack_00000018 +
                   fStack_124 * in_stack_00000018[1] + fStack_120 * in_stack_00000018[2];
      (**(code **)*in_stack_0000000c)(auStack_f4);
      Vec3__SetXYZ();
      *in_stack_00000018 = fStack_110;
      in_stack_00000018[1] = fStack_10c;
      in_stack_00000018[2] = fStack_108;
      in_stack_00000018[3] = fStack_104;
    }
    pfVar5 = (float *)&DAT_00704d20;
    for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
      *pfVar5 = *in_stack_00000014;
      in_stack_00000014 = in_stack_00000014 + 1;
      pfVar5 = pfVar5 + 1;
    }
    DAT_00704ce0 = *in_stack_00000018;
    DAT_00704ce4 = in_stack_00000018[1];
    DAT_00704ce8 = in_stack_00000018[2];
    DAT_00704cec = in_stack_00000018[3];
    DAT_00704d54 = in_stack_00000004;
    DAT_00704d5c = local_158;
    DAT_00704da4 = local_114;
    DAT_00704da0 = in_stack_00000010;
    return (int)in_stack_00000010;
  }
  if (*(int *)(in_ECX + 0x98) == 0) {
    pfVar5 = (float *)Vec3__SetXYZ();
    afStack_e0[0] = *pfVar5;
    afStack_e0[1] = pfVar5[1];
    afStack_e0[2] = pfVar5[2];
    afStack_e0[3] = pfVar5[3];
    puVar6 = (undefined4 *)Vec3__SetXYZ();
    uStack_d0 = *puVar6;
    uStack_cc = puVar6[1];
    uStack_c8 = puVar6[2];
    uStack_c4 = puVar6[3];
    puVar6 = (undefined4 *)Vec3__SetXYZ();
    uStack_c0 = *puVar6;
    uStack_bc = puVar6[1];
    uStack_b8 = puVar6[2];
    afStack_b4[0] = (float)puVar6[3];
    fStack_16c = 0.0;
    fStack_168 = 0.0;
    fStack_164 = 0.0;
  }
  else {
    CMCMech__Helper_004b0fb0();
  }
  CMeshPart__Unk_004b0d00();
  if (in_stack_00000010 != (int *)0x0) {
    piVar7 = (int *)(**(code **)(*in_stack_00000010 + 0x70))();
    if ((piVar7 != (int *)0x0) && (in_stack_00000020 != '\0')) {
      (**(code **)(*piVar7 + 0xc))();
    }
    if ((cVar10 == '\0') && (*(int *)(in_ECX + 0x88) == 0)) {
      iVar3 = (**(code **)*in_stack_00000010)(auStack_f0);
      fStack_16c = fStack_16c + *(float *)(iVar3 + 4);
      fStack_168 = fStack_168 + *(float *)(iVar3 + 8);
      pvVar12 = (void *)(**(code **)(*in_stack_00000010 + 4))(afStack_b4);
      CMCBuggy__Helper_0040d320(afStack_e0,auStack_80,pvVar12,unaff_EDI);
      pfVar5 = extraout_EAX_02;
      pfVar9 = afStack_e0;
      for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
        *pfVar9 = *pfVar5;
        pfVar5 = pfVar5 + 1;
        pfVar9 = pfVar9 + 1;
      }
    }
  }
  CSquadNormal__Helper_0040d2c0(afStack_e0,auStack_f0,in_stack_00000018,unaff_EDI);
  fStack_16c = fStack_16c + *extraout_EAX_03;
  fStack_168 = fStack_168 + extraout_EAX_03[1];
  fStack_164 = fStack_164 + extraout_EAX_03[2];
  CMCBuggy__Helper_0040d320(afStack_e0,afStack_b4 + 1,in_stack_00000014,unaff_EDI);
  pfVar5 = extraout_EAX_04;
  pfVar9 = afStack_e0;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *pfVar9 = *pfVar5;
    pfVar5 = pfVar5 + 1;
    pfVar9 = pfVar9 + 1;
  }
  if (((in_stack_00000010 != (int *)0x0) &&
      (piVar7 = (int *)(**(code **)(*in_stack_00000010 + 0x70))(), piVar7 != (int *)0x0)) &&
     (in_stack_00000020 != '\0')) {
    (**(code **)(*piVar7 + 0x10))(local_114,&fStack_16c,afStack_e0,in_stack_0000001c);
  }
  *in_stack_00000018 = fStack_16c;
  in_stack_00000018[1] = fStack_168;
  in_stack_00000018[2] = fStack_164;
  in_stack_00000018[3] = fStack_160;
  pfVar5 = afStack_e0;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *in_stack_00000014 = *pfVar5;
    pfVar5 = pfVar5 + 1;
    in_stack_00000014 = in_stack_00000014 + 1;
  }
  iVar3 = 0xc;
  if (cVar10 != '\0') {
    DAT_00704cd0 = fStack_16c;
    DAT_00704cd4 = fStack_168;
    DAT_00704cd8 = fStack_164;
    DAT_00704da0 = in_stack_00000010;
    pfVar5 = afStack_e0;
    pfVar9 = (float *)&DAT_00704cf0;
    for (; iVar3 != 0; iVar3 = iVar3 + -1) {
      *pfVar9 = *pfVar5;
      pfVar5 = pfVar5 + 1;
      pfVar9 = pfVar9 + 1;
    }
    DAT_00704cdc = fStack_160;
    DAT_00704d50 = in_stack_00000004;
    DAT_00704d58 = local_158;
    return (int)local_158;
  }
  DAT_00704ce4 = fStack_168;
  DAT_00704ce0 = fStack_16c;
  DAT_00704ce8 = fStack_164;
  DAT_00704da0 = in_stack_00000010;
  pfVar5 = afStack_e0;
  pfVar9 = (float *)&DAT_00704d20;
  for (; iVar3 != 0; iVar3 = iVar3 + -1) {
    *pfVar9 = *pfVar5;
    pfVar5 = pfVar5 + 1;
    pfVar9 = pfVar9 + 1;
  }
  DAT_00704cec = fStack_160;
  DAT_00704d54 = in_stack_00000004;
  DAT_00704d5c = local_158;
  return (int)fStack_160;
}
