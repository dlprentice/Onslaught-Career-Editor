/* address: 0x004b0d00 */
/* name: CMeshPart__InterpolateSegmentTransform */
/* signature: int CMeshPart__InterpolateSegmentTransform(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__InterpolateSegmentTransform(void)

{
  byte bVar1;
  byte bVar2;
  float *pfVar3;
  float extraout_EAX;
  int iVar4;
  int in_ECX;
  float *pfVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int in_stack_00000004;
  int in_stack_00000008;
  void *in_stack_0000000c;
  undefined4 *in_stack_00000010;
  float *in_stack_00000014;
  float local_128;
  float local_124;
  float local_120;
  float local_11c;
  byte local_118;
  undefined3 uStack_117;
  byte local_114;
  undefined3 uStack_113;
  float local_10c;
  float local_108;
  undefined1 local_100 [48];
  undefined1 local_d0 [16];
  undefined1 local_c0 [16];
  undefined1 local_b0 [16];
  undefined1 local_a0 [48];
  undefined1 local_70 [16];
  undefined1 local_60 [16];
  undefined1 local_50 [16];
  undefined1 local_40 [16];
  undefined4 local_30 [12];

  iVar4 = *(int *)(in_ECX + 0xb8);
  if (iVar4 <= in_stack_00000004) {
    in_stack_00000004 = iVar4 + -1;
  }
  if (iVar4 <= in_stack_00000008) {
    in_stack_00000008 = iVar4 + -1;
  }
  bVar1 = *(byte *)(*(int *)(in_ECX + 0xc4) + in_stack_00000004);
  bVar2 = *(byte *)(*(int *)(in_ECX + 0xc4) + in_stack_00000008);
  _local_114 = CONCAT31(uStack_113,bVar2);
  iVar4 = *(int *)(in_ECX + 200);
  _local_118 = CONCAT31(uStack_117,bVar1);
  pfVar3 = (float *)((uint)bVar2 * 0x10 + iVar4);
  iVar7 = (uint)bVar1 * 0x10;
  pfVar5 = (float *)(iVar4 + iVar7);
  iVar6 = (uint)bVar1 * 0x30;
  local_10c = (pfVar3[1] - *(float *)(iVar4 + 4 + iVar7)) * (float)in_stack_0000000c;
  local_108 = (pfVar3[2] - pfVar5[2]) * (float)in_stack_0000000c;
  local_128 = (*pfVar3 - *(float *)(iVar4 + iVar7)) * (float)in_stack_0000000c + *pfVar5;
  local_124 = local_10c + pfVar5[1];
  local_120 = local_108 + pfVar5[2];
  *in_stack_00000014 = local_128;
  in_stack_00000014[1] = local_124;
  in_stack_00000014[2] = local_120;
  in_stack_00000014[3] = local_11c;
  iVar4 = *(int *)(in_ECX + 0x10c);
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  CMeshCollisionVolume__Helper_0040d120
            ((void *)((uint)bVar2 * 0x30 + iVar4),local_50,(void *)(iVar6 + iVar4),&local_128);
  Mat34__SetRows();
  Vec3__SetXYZ();
  CExplosionInitThing__Helper_0040d150(local_a0,local_60,in_stack_0000000c,(float)local_c0);
  CExplosionInitThing__Helper_0040d150(local_b0,local_70,in_stack_0000000c,extraout_EAX);
  Mat34__SetRows();
  iVar4 = *(int *)(in_ECX + 0x10c);
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__Add((void *)(iVar6 + iVar4),local_40,local_100,local_d0);
  iVar4 = Mat34__SetRows();
  puVar8 = local_30;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *in_stack_00000010 = *puVar8;
    puVar8 = puVar8 + 1;
    in_stack_00000010 = in_stack_00000010 + 1;
  }
  return iVar4;
}
