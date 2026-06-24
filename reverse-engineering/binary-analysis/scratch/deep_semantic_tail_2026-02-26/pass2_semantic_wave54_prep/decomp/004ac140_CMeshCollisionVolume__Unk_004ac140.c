/* address: 0x004ac140 */
/* name: CMeshCollisionVolume__Unk_004ac140 */
/* signature: int CMeshCollisionVolume__Unk_004ac140(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshCollisionVolume__Unk_004ac140(void)

{
  float *pfVar1;
  float *pfVar2;
  float *pfVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  undefined4 *puVar7;
  double dVar8;
  undefined4 in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;
  int local_4c;
  float local_20;
  float local_1c;
  float local_18;
  float local_10;
  float local_c;
  float local_8;
  float local_4;

  if (DAT_00704cc8 == 0) {
    CMeshCollisionVolume__Unk_004ac000();
  }
  local_4c = 0;
  fVar4 = (*in_stack_0000000c + *in_stack_00000010) - *in_stack_0000000c;
  local_c = (in_stack_00000010[1] + in_stack_0000000c[1]) - in_stack_0000000c[1];
  local_8 = (in_stack_00000010[2] + in_stack_0000000c[2]) - in_stack_0000000c[2];
  pfVar2 = *(float **)(in_stack_00000008 + 0xfc);
  pfVar1 = pfVar2 + 4;
  fVar5 = SQRT(fVar4 * fVar4 + local_c * local_c + local_8 * local_8) * _DAT_005d85ec +
          *in_stack_00000014;
  local_20 = (fVar4 * _DAT_005d85ec + *in_stack_0000000c) - *pfVar2;
  local_1c = (local_c * _DAT_005d85ec + in_stack_0000000c[1]) - pfVar2[1];
  local_18 = (local_8 * _DAT_005d85ec + in_stack_0000000c[2]) - pfVar2[2];
  if ((((local_20 - fVar5 <= *pfVar1) && (-*pfVar1 <= local_20 + fVar5)) &&
      (local_1c - fVar5 <= pfVar2[5])) &&
     (((-pfVar2[5] <= local_1c + fVar5 && (local_18 - fVar5 <= pfVar2[6])) &&
      (-pfVar2[6] <= local_18 + fVar5)))) {
    if (*(int *)(in_stack_00000018 + 0xcc) != 0) {
      puVar7 = &DAT_00704bfc;
      do {
        pfVar3 = (float *)puVar7[-1];
        local_4 = pfVar3[3];
        local_10 = *pfVar3 * *pfVar1 + *pfVar2;
        local_c = pfVar3[1] * pfVar2[5] + pfVar2[1];
        local_8 = pfVar3[2] * pfVar2[6] + pfVar2[2];
        iVar6 = CMeshCollisionVolume__Helper_00478510();
        if (iVar6 != 0) {
          local_4c = 1;
        }
        puVar7 = puVar7 + 3;
      } while ((int)puVar7 < 0x704c5c);
      if (local_4c != 1) {
        return local_4c;
      }
      *(undefined4 *)(in_stack_00000018 + 0xe4) = in_stack_00000004;
      return 1;
    }
    dVar8 = CMeshCollisionVolume__Helper_00479770(&local_20,pfVar1);
    if ((float)dVar8 - fVar5 <= _DAT_005d856c) {
      *(float *)(in_stack_00000018 + 0xc4) = (float)dVar8 - fVar5;
      *(undefined4 *)(in_stack_00000018 + 0xe4) = in_stack_00000004;
      *(undefined4 *)(in_stack_00000018 + 0xa8) = 1;
      *(undefined4 *)(in_stack_00000018 + 0x94) = 1;
      return 1;
    }
  }
  return 0;
}
