/* address: 0x004b5330 */
/* name: CMeshPart__EvaluateAnimatedTransformCore */
/* signature: int CMeshPart__EvaluateAnimatedTransformCore(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__EvaluateAnimatedTransformCore(void)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  float *pfVar4;
  int iVar5;
  float *pfVar6;
  int iVar7;
  void *unaff_EDI;
  float10 fVar8;
  double dVar9;
  int *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  int *in_stack_00000014;
  undefined4 *in_stack_00000018;
  float local_174;
  void *pvStack_170;
  int iStack_16c;
  float fStack_168;
  float fStack_164;
  float fStack_160;
  float fStack_15c;
  undefined8 uStack_158;
  float fStack_150;
  undefined4 uStack_14c;
  int *local_148;
  float afStack_144 [13];
  float fStack_110;
  float fStack_10c;
  byte bStack_104;
  undefined3 uStack_103;
  undefined1 auStack_100 [48];
  undefined1 auStack_d0 [48];
  undefined1 auStack_a0 [32];
  undefined1 auStack_80 [32];
  undefined1 auStack_60 [16];
  undefined1 auStack_50 [16];
  undefined1 auStack_40 [16];
  float afStack_30 [12];

  local_148 = (int *)0x0;
  if (in_stack_00000004 != (int *)0x0) {
    local_148 = (int *)(**(code **)(*in_stack_00000004 + 0x70))();
  }
  piVar2 = local_148;
  iVar3 = -1;
  local_174 = 0.0;
  if (in_stack_00000004 != (int *)0x0) {
    iVar3 = (**(code **)(*in_stack_00000004 + 0x1c))();
  }
  if (((byte)*in_stack_00000018 & 8) == 8) {
    iVar3 = DAT_00704e5c;
  }
  if (((*(int *)(in_stack_00000010 + 0xb8) < 2) ||
      (*(int *)(*(int *)(in_stack_00000010 + 0x128) + 0x14) == 0)) || (iVar3 < 0)) {
    if (piVar2 != (int *)0x0) {
      (**(code **)(*piVar2 + 0x14))(in_stack_00000010,&local_174);
    }
    dVar9 = CDXEngine__Helper_0055dfe7((double)local_174);
    uStack_158 = (longlong)ROUND(dVar9);
  }
  else {
    iVar3 = *(int *)(*(int *)(in_stack_00000010 + 0x128) + 0x18) + iVar3 * 0x24;
    if (iVar3 == 0) {
      DebugTrace(s_Warning___got_null_animmode_in_m_00630138);
      if (piVar2 != (int *)0x0) {
        (**(code **)(*piVar2 + 0x14))(in_stack_00000010,&local_174);
      }
      dVar9 = CDXEngine__Helper_0055dfe7((double)local_174);
      uStack_158 = (longlong)ROUND(dVar9);
    }
    else {
      if (in_stack_00000004 != (int *)0x0) {
        fVar8 = (float10)(**(code **)(*in_stack_00000004 + 0x18))();
        local_174 = (float)fVar8;
      }
      if (((byte)*in_stack_00000018 & 8) == 8) {
        local_174 = DAT_00704e58;
      }
      local_174 = (float)*(int *)(iVar3 + 0x14) + (float)*(int *)(iVar3 + 0x1c) * local_174;
      if (piVar2 != (int *)0x0) {
        (**(code **)(*piVar2 + 0x14))(in_stack_00000010,&local_174);
      }
      dVar9 = CDXEngine__Helper_0055dfe7((double)local_174);
      uStack_158 = (longlong)ROUND(dVar9);
    }
  }
  iStack_16c = (uint)uStack_158;
  dVar9 = CDXEngine__Helper_0055dfe7((double)local_174);
  pvStack_170 = (void *)(local_174 - (float)dVar9);
  if (*(int *)(in_stack_00000010 + 0xb8) <= iStack_16c) {
    iStack_16c = *(int *)(in_stack_00000010 + 0xb8) + -1;
  }
  if (piVar2 != (int *)0x0) {
    (**(code **)(*piVar2 + 0xc))(in_stack_00000010,in_stack_00000008,in_stack_0000000c);
  }
  iVar3 = 1;
  if (piVar2 != (int *)0x0) {
    iVar3 = (**(code **)(*piVar2 + 0x24))();
  }
  iVar5 = iStack_16c + 1;
  if (*(int *)(in_stack_00000010 + 0xb8) <= iVar5) {
    if (iVar3 == 0) {
      iVar5 = *(int *)(in_stack_00000010 + 0xb8) + -1;
    }
    else {
      iVar5 = 0;
    }
  }
  bVar1 = *(byte *)(*(int *)(in_stack_00000010 + 0xc4) + iVar5);
  uStack_158._0_4_ = (uint)*(byte *)(*(int *)(in_stack_00000010 + 0xc4) + iStack_16c);
  _bStack_104 = CONCAT31(uStack_103,bVar1);
  iVar3 = *(int *)(in_stack_00000010 + 200);
  pfVar4 = (float *)((uint)bVar1 * 0x10 + iVar3);
  iVar5 = (uint)uStack_158 * 0x10;
  pfVar6 = (float *)(iVar3 + iVar5);
  iVar7 = (uint)uStack_158 * 0x30;
  fStack_110 = (pfVar4[1] - *(float *)(iVar3 + 4 + iVar5)) * (float)pvStack_170;
  fStack_10c = (pfVar4[2] - pfVar6[2]) * (float)pvStack_170;
  fStack_168 = (*pfVar4 - *(float *)(iVar3 + iVar5)) * (float)pvStack_170 + *pfVar6;
  fStack_164 = fStack_110 + pfVar6[1];
  uStack_158 = CONCAT44(fStack_164,fStack_168);
  fStack_160 = fStack_10c + pfVar6[2];
  fStack_15c = (float)uStack_14c;
  iVar3 = *(int *)(in_stack_00000010 + 0x10c);
  fStack_150 = fStack_160;
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  CMeshCollisionVolume__Helper_0040d120
            ((void *)((uint)bVar1 * 0x30 + iVar3),auStack_80,(void *)(iVar7 + iVar3),&uStack_158);
  Mat34__SetRows();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  CExplosionInitThing__Helper_0040d150(auStack_d0,auStack_40,pvStack_170,(float)auStack_a0);
  Mat34__SetRows();
  iVar3 = *(int *)(in_stack_00000010 + 0x10c);
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__Add((void *)(iVar7 + iVar3),auStack_60,auStack_100,auStack_50);
  Mat34__SetRows();
  pfVar4 = afStack_30;
  pfVar6 = afStack_144;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *pfVar6 = *pfVar4;
    pfVar4 = pfVar4 + 1;
    pfVar6 = pfVar6 + 1;
  }
  if ((in_stack_00000004 == (int *)0x0) ||
     (iVar3 = (**(code **)(*in_stack_00000004 + 0x38))(), iVar3 != 0)) {
    fStack_110 = fStack_168 * in_stack_0000000c[4] +
                 fStack_160 * in_stack_0000000c[6] + fStack_164 * in_stack_0000000c[5];
    fStack_10c = fStack_160 * in_stack_0000000c[10] +
                 fStack_164 * in_stack_0000000c[9] + fStack_168 * in_stack_0000000c[8];
    *in_stack_00000008 =
         fStack_164 * in_stack_0000000c[1] +
         fStack_160 * in_stack_0000000c[2] + fStack_168 * *in_stack_0000000c + *in_stack_00000008;
    in_stack_00000008[1] = fStack_110 + in_stack_00000008[1];
    in_stack_00000008[2] = fStack_10c + in_stack_00000008[2];
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    pfVar4 = afStack_30;
  }
  else {
    CMCTentacle__Helper_0041ad10(in_stack_00000008,&fStack_168,unaff_EDI);
    pfVar4 = afStack_144;
  }
  piVar2 = local_148;
  pfVar6 = in_stack_0000000c;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *pfVar6 = *pfVar4;
    pfVar4 = pfVar4 + 1;
    pfVar6 = pfVar6 + 1;
  }
  if (local_148 != (int *)0x0) {
    (**(code **)(*local_148 + 0x10))(in_stack_00000010,in_stack_00000008,in_stack_0000000c,1);
    (**(code **)(*piVar2 + 0x18))(in_stack_00000010,in_stack_00000008);
  }
  *in_stack_00000014 = in_stack_00000010;
  fStack_168 = *in_stack_00000008;
  fStack_164 = in_stack_00000008[1];
  fStack_160 = in_stack_00000008[2];
  fStack_15c = in_stack_00000008[3];
  pfVar4 = in_stack_0000000c;
  pfVar6 = afStack_144;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *pfVar6 = *pfVar4;
    pfVar4 = pfVar4 + 1;
    pfVar6 = pfVar6 + 1;
  }
  if ((piVar2 != (int *)0x0) && (iVar3 = (**(code **)(*piVar2 + 0x1c))(), iVar3 != 0)) {
    if (0 < iVar3) {
      do {
        iVar3 = iVar3 + -1;
        *in_stack_00000014 = *(int *)(*in_stack_00000014 + 0x9c);
      } while (iVar3 != 0);
    }
    CMCMech__Helper_004b0fb0();
  }
  *in_stack_00000008 = fStack_168;
  in_stack_00000008[1] = fStack_164;
  in_stack_00000008[2] = fStack_160;
  in_stack_00000008[3] = fStack_15c;
  pfVar4 = afStack_144;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *in_stack_0000000c = *pfVar4;
    pfVar4 = pfVar4 + 1;
    in_stack_0000000c = in_stack_0000000c + 1;
  }
  return (int)in_stack_00000008;
}
