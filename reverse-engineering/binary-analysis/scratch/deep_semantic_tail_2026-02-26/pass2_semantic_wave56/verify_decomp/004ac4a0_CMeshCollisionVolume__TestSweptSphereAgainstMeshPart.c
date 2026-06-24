/* address: 0x004ac4a0 */
/* name: CMeshCollisionVolume__TestSweptSphereAgainstMeshPart */
/* signature: int CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void)

{
  int iVar1;
  float fVar2;
  int iVar3;
  float *pfVar4;
  void *unaff_EDI;
  undefined4 in_stack_00000004;
  void *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;
  int local_54;
  short *local_50;
  short *local_4c;
  short *local_48;
  float local_40;
  float local_3c;
  float local_38;
  float local_30;
  float local_2c;
  float local_28;
  float local_20;
  float local_1c;
  float local_18;
  float local_10;
  float local_c;
  float local_8;

  local_4c = (short *)(in_stack_00000010[1] + in_stack_0000000c[1]);
  local_48 = (short *)(in_stack_00000010[2] + in_stack_0000000c[2]);
  local_54 = 0;
  local_3c = (float)local_4c + in_stack_0000000c[1];
  local_38 = (float)local_48 + in_stack_0000000c[2];
  local_30 = (*in_stack_0000000c + *in_stack_00000010 + *in_stack_0000000c) * _DAT_005d85ec;
  local_2c = local_3c * _DAT_005d85ec;
  local_28 = local_38 * _DAT_005d85ec;
  fVar2 = (*in_stack_0000000c + *in_stack_00000010) - *in_stack_0000000c;
  iVar3 = CMeshPart__Unk_004ae110
                    (in_stack_00000008,(int)&local_30,
                     (int)(SQRT(fVar2 * fVar2 +
                                ((float)local_4c - in_stack_0000000c[1]) *
                                ((float)local_4c - in_stack_0000000c[1]) +
                                ((float)local_48 - in_stack_0000000c[2]) *
                                ((float)local_48 - in_stack_0000000c[2])) * _DAT_005d85ec +
                          *in_stack_00000014),(int)&local_50,unaff_EDI);
  iVar1 = *(int *)((int)in_stack_00000008 + 0x100);
  pfVar4 = (float *)(iVar1 + 0x40);
  if (iVar3 != 1) {
    return 0;
  }
  do {
    local_10 = (float)(int)*local_50 * *(float *)(iVar1 + 0x50) * _DAT_005d8618 + *pfVar4;
    local_c = (float)(int)local_50[1] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
              *(float *)(iVar1 + 0x44);
    local_8 = (float)(int)local_50[2] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
              *(float *)(iVar1 + 0x48);
    local_20 = (float)(int)*local_4c * *(float *)(iVar1 + 0x50) * _DAT_005d8618 + *pfVar4;
    local_1c = (float)(int)local_4c[1] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
               *(float *)(iVar1 + 0x44);
    local_18 = (float)(int)local_4c[2] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
               *(float *)(iVar1 + 0x48);
    local_40 = (float)(int)*local_48 * *(float *)(iVar1 + 0x50) * _DAT_005d8618 + *pfVar4;
    local_3c = (float)(int)local_48[1] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
               *(float *)(iVar1 + 0x44);
    local_38 = (float)(int)local_48[2] * *(float *)(iVar1 + 0x50) * _DAT_005d8618 +
               *(float *)(iVar1 + 0x48);
    iVar3 = CMeshCollisionVolume__Helper_00478510();
    if (iVar3 != 0) {
      local_54 = 1;
      *(undefined4 *)(in_stack_00000018 + 0xe4) = in_stack_00000004;
    }
    iVar3 = CMeshPart__Unk_004ae1a0(in_stack_00000008,(int)&local_50,unaff_EDI);
  } while (iVar3 == 1);
  return local_54;
}
