/* address: 0x00478c20 */
/* name: Geometry__IntersectSegmentTriangleAndStoreHit */
/* signature: int Geometry__IntersectSegmentTriangleAndStoreHit(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Geometry__IntersectSegmentTriangleAndStoreHit(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  void *unaff_EDI;
  double dVar8;
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;
  float local_40;
  float local_3c;
  float local_38;
  undefined4 local_34;
  float local_30;
  float local_2c;
  float local_28;
  undefined4 local_24;
  float local_20;
  float local_1c;
  float local_10;
  float local_c;
  float local_8;

  fVar1 = in_stack_00000008[1] - in_stack_00000004[1];
  fVar2 = in_stack_00000008[2] - in_stack_00000004[2];
  local_40 = (in_stack_0000000c[2] - in_stack_00000004[2]) * fVar1 -
             (in_stack_0000000c[1] - in_stack_00000004[1]) * fVar2;
  fVar3 = *in_stack_00000008 - *in_stack_00000004;
  local_3c = (*in_stack_0000000c - *in_stack_00000004) * fVar2 -
             fVar3 * (in_stack_0000000c[2] - in_stack_00000004[2]);
  local_38 = fVar3 * (in_stack_0000000c[1] - in_stack_00000004[1]) -
             (*in_stack_0000000c - *in_stack_00000004) * fVar1;
  fVar4 = SQRT(local_38 * local_38 + local_3c * local_3c + local_40 * local_40);
  if (fVar4 != _DAT_005d856c) {
    fVar4 = _DAT_005d8568 / fVar4;
    local_40 = fVar4 * local_40;
    local_3c = fVar4 * local_3c;
    local_38 = fVar4 * local_38;
  }
  fVar4 = *in_stack_00000014 - *in_stack_00000010;
  fVar5 = in_stack_00000014[1] - in_stack_00000010[1];
  fVar6 = in_stack_00000014[2] - in_stack_00000010[2];
  if (((((fVar5 * local_3c + fVar4 * local_40 + fVar6 * local_38 <= (float)_DAT_005d87b0) &&
        (fVar7 = fVar4 * local_40 + fVar5 * local_3c + fVar6 * local_38, _DAT_005d8cb0 <= ABS(fVar7)
        )) && (fVar7 = -((local_3c * in_stack_00000010[1] +
                         local_38 * in_stack_00000010[2] +
                         local_40 * *in_stack_00000010 +
                         ((-(local_40 * *in_stack_00000004) - local_3c * in_stack_00000004[1]) -
                         local_38 * in_stack_00000004[2])) / fVar7), _DAT_005d856c <= fVar7)) &&
      (fVar7 <= _DAT_005d8568)) &&
     (((in_stack_00000018 == 0 || (*(int *)(in_stack_00000018 + 0xa8) == 0)) ||
      (fVar7 <= *(float *)(in_stack_00000018 + 0xc4))))) {
    local_30 = fVar4 * fVar7 + *in_stack_00000010;
    local_2c = fVar5 * fVar7 + in_stack_00000010[1];
    local_28 = fVar6 * fVar7 + in_stack_00000010[2];
    if (((float)_DAT_005d87b0 <=
         (fVar2 * (in_stack_00000004[1] - local_2c) - fVar1 * (in_stack_00000004[2] - local_28)) *
         local_40 +
         ((in_stack_00000004[2] - local_28) * fVar3 - fVar2 * (*in_stack_00000004 - local_30)) *
         local_3c +
         (fVar1 * (*in_stack_00000004 - local_30) - (in_stack_00000004[1] - local_2c) * fVar3) *
         local_38) &&
       ((float)_DAT_005d87b0 <=
        ((in_stack_0000000c[2] - in_stack_00000008[2]) * (in_stack_00000008[1] - local_2c) -
        (in_stack_0000000c[1] - in_stack_00000008[1]) * (in_stack_00000008[2] - local_28)) *
        local_40 +
        ((in_stack_00000008[2] - local_28) * (*in_stack_0000000c - *in_stack_00000008) -
        (in_stack_0000000c[2] - in_stack_00000008[2]) * (*in_stack_00000008 - local_30)) * local_3c
        + ((in_stack_0000000c[1] - in_stack_00000008[1]) * (*in_stack_00000008 - local_30) -
          (in_stack_00000008[1] - local_2c) * (*in_stack_0000000c - *in_stack_00000008)) * local_38)
       ) {
      local_20 = *in_stack_00000004 - *in_stack_0000000c;
      local_1c = in_stack_00000004[1] - in_stack_0000000c[1];
      local_10 = (in_stack_00000004[2] - in_stack_0000000c[2]) * (in_stack_0000000c[1] - local_2c) -
                 local_1c * (in_stack_0000000c[2] - local_28);
      local_c = (in_stack_0000000c[2] - local_28) * local_20 -
                (in_stack_00000004[2] - in_stack_0000000c[2]) * (*in_stack_0000000c - local_30);
      local_8 = local_1c * (*in_stack_0000000c - local_30) -
                (in_stack_0000000c[1] - local_2c) * local_20;
      dVar8 = CMeshCollisionVolume__Helper_0040d180(&local_40,&local_10,unaff_EDI);
      if (_DAT_005d87b0 <= dVar8) {
        if (in_stack_00000018 == 0) {
          return 1;
        }
        *(float *)(in_stack_00000018 + 0xc4) = fVar7;
        *(float *)(in_stack_00000018 + 0x84) = local_30;
        *(undefined4 *)(in_stack_00000018 + 0xa8) = 1;
        *(undefined4 *)(in_stack_00000018 + 0x94) = 1;
        *(float *)(in_stack_00000018 + 0x88) = local_2c;
        *(float *)(in_stack_00000018 + 0x8c) = local_28;
        *(undefined4 *)(in_stack_00000018 + 0x90) = local_24;
        *(float *)(in_stack_00000018 + 0xd4) = local_40;
        *(float *)(in_stack_00000018 + 0xd8) = local_3c;
        *(float *)(in_stack_00000018 + 0xdc) = local_38;
        *(undefined4 *)(in_stack_00000018 + 0xe0) = local_34;
        return 1;
      }
    }
  }
  return 0;
}
