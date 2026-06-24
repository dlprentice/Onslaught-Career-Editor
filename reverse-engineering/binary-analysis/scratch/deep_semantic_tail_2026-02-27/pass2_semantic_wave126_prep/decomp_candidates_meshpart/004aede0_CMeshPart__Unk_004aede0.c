/* address: 0x004aede0 */
/* name: CMeshPart__Unk_004aede0 */
/* signature: int CMeshPart__Unk_004aede0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMeshPart__Unk_004aede0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  void *pvVar6;
  float *pfVar7;
  int extraout_EAX;
  float *in_ECX;
  int iVar8;
  int iVar9;
  undefined4 *puVar10;
  int iVar11;
  int unaff_EDI;
  int iVar12;
  void *in_stack_00000004;
  int in_stack_00000010;
  int local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;

  pvVar6 = in_stack_00000004;
  iVar11 = 0;
  if (0 < (int)in_ECX[0x2a]) {
    iVar12 = 0;
    do {
      DXMemBuffer__ReadBytes(iVar12 + 0x20 + (int)in_ECX[0x4d],4);
      DXMemBuffer__ReadBytes(iVar12 + 0x24 + (int)in_ECX[0x4d],4);
      DXMemBuffer__ReadBytes(iVar12 + 0x28 + (int)in_ECX[0x4d],4);
      *(float *)(iVar12 + 0x28 + (int)in_ECX[0x4d]) = -*(float *)(iVar12 + 0x28 + (int)in_ECX[0x4d])
      ;
      DXMemBuffer__ReadBytes(iVar12 + 0x2c + (int)in_ECX[0x4d],4);
      DXMemBuffer__ReadBytes(&stack0x00000004,4);
      if (((int)in_stack_00000004 < -2) || (in_stack_00000010 <= (int)in_stack_00000004)) {
        in_stack_00000004 = (void *)0xffffffff;
      }
      iVar8 = 6;
      iVar9 = iVar12 + 0x30;
      do {
        iVar8 = iVar8 + -1;
        *(undefined4 *)(iVar9 + (int)in_ECX[0x4d]) = 0xffffffff;
        iVar9 = iVar9 + 4;
      } while (iVar8 != 0);
      if (in_stack_00000004 == (void *)0xffffffff) {
        *(undefined4 *)(iVar12 + 0x30 + (int)in_ECX[0x4d]) = 0;
      }
      else {
        *(void **)(iVar12 + 0x30 + (int)in_ECX[0x4d]) = in_stack_00000004;
      }
      local_20 = 1.0;
      puVar10 = (undefined4 *)(iVar12 + (int)in_ECX[0x4d]);
      local_1c = 0.0;
      *puVar10 = 0x3f800000;
      local_18 = 0.0;
      puVar10[1] = 0;
      iVar11 = iVar11 + 1;
      iVar12 = iVar12 + 0x60;
      puVar10[2] = 0;
      puVar10[3] = local_14;
    } while (iVar11 < (int)in_ECX[0x2a]);
  }
  iVar11 = 0;
  in_stack_00000010 = 0;
  if (0 < (int)in_ECX[0x2d]) {
    do {
      iVar12 = 0;
      if (0 < (int)in_ECX[0x2b]) {
        in_stack_00000004 = (void *)0x0;
        do {
          CMesh__Helper_0044c1c0
                    ((void *)(*(int *)(iVar11 + (int)in_ECX[0x21]) + (int)in_stack_00000004),pvVar6,
                     unaff_EDI);
          iVar12 = iVar12 + 1;
          in_stack_00000004 = (void *)((int)in_stack_00000004 + 0x10);
        } while (iVar12 < (int)in_ECX[0x2b]);
      }
      iVar12 = 0;
      if (0 < (int)in_ECX[0x2b]) {
        iVar9 = 0;
        do {
          pfVar7 = (float *)(*(int *)(iVar11 + (int)in_ECX[0x21]) + iVar9);
          *pfVar7 = *pfVar7 - in_ECX[0x18];
          pfVar7[1] = pfVar7[1] - in_ECX[0x19];
          pfVar7[2] = pfVar7[2] - in_ECX[0x1a];
          fVar1 = in_ECX[2];
          fVar2 = in_ECX[6];
          fVar3 = in_ECX[10];
          local_10 = *in_ECX;
          local_c = in_ECX[4];
          iVar8 = *(int *)(iVar11 + (int)in_ECX[0x21]);
          local_8 = in_ECX[8];
          pfVar7 = (float *)(iVar8 + iVar9);
          local_20 = local_8 * pfVar7[2] +
                     local_c * *(float *)(iVar8 + 4 + iVar9) + local_10 * *(float *)(iVar8 + iVar9);
          local_1c = in_ECX[9] * pfVar7[2] + in_ECX[5] * pfVar7[1] + in_ECX[1] * *pfVar7;
          fVar4 = *pfVar7;
          fVar5 = pfVar7[1];
          *pfVar7 = local_20;
          pfVar7[1] = local_1c;
          local_18 = fVar3 * pfVar7[2] + fVar2 * fVar5 + fVar1 * fVar4;
          pfVar7[2] = local_18;
          iVar12 = iVar12 + 1;
          pfVar7[3] = local_14;
          iVar9 = iVar9 + 0x10;
        } while (iVar12 < (int)in_ECX[0x2b]);
      }
      in_stack_00000010 = in_stack_00000010 + 1;
      iVar11 = iVar11 + 4;
    } while (in_stack_00000010 < (int)in_ECX[0x2d]);
  }
  iVar11 = 0;
  if (0 < (int)in_ECX[0x2c]) {
    iVar12 = 0;
    do {
      DXMemBuffer__ReadBytes(&stack0x00000004,4);
      DXMemBuffer__ReadBytes(&local_24,4);
      DXMemBuffer__ReadBytes(&stack0x00000010,4);
      *(int *)(iVar12 + (int)in_ECX[0x20]) = (int)in_stack_00000004 * 0x60 + (int)in_ECX[0x4d];
      *(int *)(iVar12 + 4 + (int)in_ECX[0x20]) = in_stack_00000010 * 0x60 + (int)in_ECX[0x4d];
      iVar11 = iVar11 + 1;
      *(int *)(iVar12 + 8 + (int)in_ECX[0x20]) = local_24 * 0x60 + (int)in_ECX[0x4d];
      iVar12 = iVar12 + 0xc;
    } while (iVar11 < (int)in_ECX[0x2c]);
  }
  CMeshPart__Unk_004b1eb0(in_ECX,1,unaff_EDI);
  return extraout_EAX;
}
