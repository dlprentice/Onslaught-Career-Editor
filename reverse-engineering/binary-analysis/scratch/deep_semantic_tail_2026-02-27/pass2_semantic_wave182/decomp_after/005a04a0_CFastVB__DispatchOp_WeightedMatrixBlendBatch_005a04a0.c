/* address: 0x005a04a0 */
/* name: CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0 */
/* signature: int CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0(void)

{
  int *piVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined8 *puVar5;
  undefined1 auVar6 [16];
  int iVar7;
  undefined1 (*pauVar8) [16];
  int *piVar9;
  float *pfVar10;
  uint uVar11;
  uint uVar12;
  undefined4 *puVar13;
  float *pfVar14;
  undefined4 *puVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  undefined1 auVar25 [16];
  undefined1 auVar26 [16];
  undefined1 auVar27 [16];
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  int in_stack_00000004;
  int in_stack_00000008;
  float *in_stack_0000000c;
  undefined8 *in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  float *in_stack_0000001c;
  int *in_stack_00000020;
  uint in_stack_00000024;
  int in_stack_00000028;
  float *in_stack_0000002c;
  int in_stack_00000030;
  float *local_4b0;
  undefined4 *local_4ac;
  undefined4 *local_4a8;
  int local_4a4;
  float local_470;
  float fStack_46c;
  float fStack_468;
  float local_420 [263];

  local_4a8 = (undefined4 *)((int)in_stack_0000000c + in_stack_00000028);
  local_4ac = (undefined4 *)((int)in_stack_00000010 + in_stack_00000028);
  uVar12 = in_stack_00000018 - in_stack_00000028;
  if (in_stack_00000008 == 0) {
    in_stack_00000008 = in_stack_00000004;
  }
  if (in_stack_00000024 == 1) {
    if (in_stack_00000014 != 0) {
      local_4b0 = (float *)(in_stack_00000010 + 1);
      local_4a4 = in_stack_00000014;
      pfVar10 = in_stack_0000000c;
      do {
        in_stack_0000000c = pfVar10;
        fVar2 = *in_stack_0000000c;
        fVar29 = 0.0;
        fVar31 = 0.0;
        fVar33 = 0.0;
        fVar3 = in_stack_0000000c[1];
        fVar4 = in_stack_0000000c[2];
        pfVar10 = (float *)*in_stack_0000001c;
        fVar19 = *pfVar10;
        fVar30 = pfVar10[1];
        fVar32 = pfVar10[2];
        fVar16 = *in_stack_0000002c;
        fVar18 = fVar29;
        fVar21 = fVar31;
        fVar23 = fVar33;
        while (-1 < (int)fVar16) {
          iVar7 = (int)*in_stack_0000002c >> 1;
          fVar16 = *in_stack_0000002c - (float)(iVar7 * 2);
          iVar7 = iVar7 * 0x40;
          pfVar10 = (float *)(in_stack_00000004 + iVar7);
          auVar26._0_4_ = pfVar10[8] * fVar4 + pfVar10[0xc];
          auVar26._4_4_ = pfVar10[9] * fVar4 + pfVar10[0xd];
          auVar26._8_4_ = pfVar10[10] * fVar4 + pfVar10[0xe];
          auVar26._12_4_ = pfVar10[0xb] * fVar4 + pfVar10[0xf];
          fVar17 = *pfVar10 * fVar2 + pfVar10[4] * fVar3 + auVar26._0_4_;
          fVar20 = pfVar10[1] * fVar2 + pfVar10[5] * fVar3 + auVar26._4_4_;
          fVar22 = pfVar10[2] * fVar2 + pfVar10[6] * fVar3 + auVar26._8_4_;
          fVar24 = pfVar10[3] * fVar2 + pfVar10[7] * fVar3 + auVar26._12_4_;
          auVar6._4_4_ = fVar20;
          auVar6._0_4_ = fVar17;
          auVar6._8_4_ = fVar22;
          auVar6._12_4_ = fVar24;
          auVar27 = rcpps(auVar26,auVar6);
          fVar28 = auVar27._12_4_;
          fVar24 = (fVar28 + fVar28) - fVar28 * fVar24 * fVar28;
          fVar29 = fVar29 + fVar17 * fVar16 * fVar24;
          fVar31 = fVar31 + fVar20 * fVar16 * fVar24;
          fVar33 = fVar33 + fVar22 * fVar16 * fVar24;
          pfVar10 = (float *)(iVar7 + in_stack_00000008);
          in_stack_0000002c = in_stack_0000002c + 1;
          fVar18 = fVar18 + (fVar19 * *pfVar10 + fVar30 * pfVar10[4] + fVar32 * pfVar10[8]) * fVar16
          ;
          fVar21 = fVar21 + (fVar19 * pfVar10[1] + fVar30 * pfVar10[5] + fVar32 * pfVar10[9]) *
                            fVar16;
          fVar23 = fVar23 + (fVar19 * pfVar10[2] + fVar30 * pfVar10[6] + fVar32 * pfVar10[10]) *
                            fVar16;
          fVar16 = *in_stack_0000002c;
        }
        if (in_stack_00000030 == 0) {
          *in_stack_00000010 = CONCAT44(fVar31,fVar29);
          *local_4b0 = fVar33;
          puVar5 = (undefined8 *)*in_stack_00000020;
          *puVar5 = CONCAT44(fVar21,fVar18);
          *(float *)(puVar5 + 1) = fVar23;
          puVar13 = local_4a8;
          puVar15 = local_4ac;
          for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
            *puVar15 = *puVar13;
            puVar13 = puVar13 + 1;
            puVar15 = puVar15 + 1;
          }
          for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
            *(undefined1 *)puVar15 = *(undefined1 *)puVar13;
            puVar13 = (undefined4 *)((int)puVar13 + 1);
            puVar15 = (undefined4 *)((int)puVar15 + 1);
          }
        }
        else {
          puVar13 = local_4a8;
          puVar15 = local_4ac;
          for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
            *puVar15 = *puVar13;
            puVar13 = puVar13 + 1;
            puVar15 = puVar15 + 1;
          }
          for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
            *(undefined1 *)puVar15 = *(undefined1 *)puVar13;
            puVar13 = (undefined4 *)((int)puVar13 + 1);
            puVar15 = (undefined4 *)((int)puVar15 + 1);
          }
          *in_stack_00000010 = CONCAT44(fVar31,fVar29);
          *local_4b0 = fVar33;
          puVar5 = (undefined8 *)*in_stack_00000020;
          *puVar5 = CONCAT44(fVar21,fVar18);
          *(float *)(puVar5 + 1) = fVar23;
        }
        *in_stack_00000020 = *in_stack_00000020 + in_stack_00000018;
        local_4ac = (undefined4 *)((int)local_4ac + in_stack_00000018);
        local_4a8 = (undefined4 *)((int)local_4a8 + in_stack_00000018);
        in_stack_00000010 = (undefined8 *)((int)in_stack_00000010 + in_stack_00000018);
        local_4b0 = (float *)((int)local_4b0 + in_stack_00000018);
        pfVar10 = (float *)((int)in_stack_0000000c + in_stack_00000018);
        *in_stack_0000001c = (float)((int)*in_stack_0000001c + in_stack_00000018);
        in_stack_0000002c = in_stack_0000002c + 1;
        local_4a4 = local_4a4 + -1;
        in_stack_0000000c = in_stack_0000001c;
      } while (local_4a4 != 0);
    }
  }
  else if (in_stack_00000014 != 0) {
    local_4b0 = (float *)(in_stack_00000010 + 1);
    local_470 = 0.0;
    fStack_46c = 0.0;
    fStack_468 = 0.0;
    local_4a4 = in_stack_00000014;
    do {
      fVar2 = *in_stack_0000000c;
      fVar3 = in_stack_0000000c[1];
      fVar4 = in_stack_0000000c[2];
      if (in_stack_00000024 != 0) {
        local_420[0] = 0.0;
        local_420[1] = 0.0;
        local_420[2] = 0.0;
        local_420[3] = 0.0;
        pfVar10 = local_420;
        pfVar14 = local_420 + 4;
        for (uVar11 = in_stack_00000024 * 0x10 - 0xd >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
          *pfVar14 = *pfVar10;
          pfVar10 = pfVar10 + 1;
          pfVar14 = pfVar14 + 1;
        }
      }
      fVar19 = *in_stack_0000002c;
      fVar30 = local_470;
      fVar32 = fStack_46c;
      fVar16 = fStack_468;
      while (-1 < (int)fVar19) {
        iVar7 = (int)*in_stack_0000002c >> 1;
        fVar19 = *in_stack_0000002c - (float)(iVar7 * 2);
        iVar7 = iVar7 * 0x40;
        pfVar10 = (float *)(in_stack_00000004 + iVar7);
        auVar25._0_4_ = pfVar10[8] * fVar4 + pfVar10[0xc];
        auVar25._4_4_ = pfVar10[9] * fVar4 + pfVar10[0xd];
        auVar25._8_4_ = pfVar10[10] * fVar4 + pfVar10[0xe];
        auVar25._12_4_ = pfVar10[0xb] * fVar4 + pfVar10[0xf];
        fVar29 = *pfVar10 * fVar2 + pfVar10[4] * fVar3 + auVar25._0_4_;
        fVar31 = pfVar10[1] * fVar2 + pfVar10[5] * fVar3 + auVar25._4_4_;
        fVar33 = pfVar10[2] * fVar2 + pfVar10[6] * fVar3 + auVar25._8_4_;
        fVar18 = pfVar10[3] * fVar2 + pfVar10[7] * fVar3 + auVar25._12_4_;
        auVar27._4_4_ = fVar31;
        auVar27._0_4_ = fVar29;
        auVar27._8_4_ = fVar33;
        auVar27._12_4_ = fVar18;
        auVar27 = rcpps(auVar25,auVar27);
        fVar21 = auVar27._12_4_;
        fVar18 = (fVar21 + fVar21) - fVar21 * fVar18 * fVar21;
        pauVar8 = (undefined1 (*) [16])(iVar7 + in_stack_00000008);
        uVar11 = 0;
        fVar30 = fVar30 + fVar29 * fVar19 * fVar18;
        fVar32 = fVar32 + fVar31 * fVar19 * fVar18;
        fVar16 = fVar16 + fVar33 * fVar19 * fVar18;
        if (in_stack_00000024 != 0) {
          fVar29 = *(float *)pauVar8[2];
          fVar31 = *(float *)(pauVar8[2] + 4);
          fVar33 = *(float *)(pauVar8[2] + 8);
          fVar18 = *(float *)(pauVar8[2] + 0xc);
          auVar27 = *pauVar8;
          fVar21 = *(float *)pauVar8[1];
          fVar23 = *(float *)(pauVar8[1] + 4);
          fVar17 = *(float *)(pauVar8[1] + 8);
          fVar20 = *(float *)(pauVar8[1] + 0xc);
          pfVar10 = local_420;
          do {
            pfVar14 = (float *)in_stack_0000001c[uVar11];
            fVar22 = pfVar14[2];
            fVar24 = pfVar14[1];
            fVar28 = *pfVar14;
            *pfVar10 = *pfVar10 +
                       (fVar28 * auVar27._0_4_ + fVar24 * fVar21 + fVar22 * fVar29) * fVar19;
            pfVar10[1] = pfVar10[1] +
                         (fVar28 * auVar27._4_4_ + fVar24 * fVar23 + fVar22 * fVar31) * fVar19;
            pfVar10[2] = pfVar10[2] +
                         (fVar28 * auVar27._8_4_ + fVar24 * fVar17 + fVar22 * fVar33) * fVar19;
            pfVar10[3] = pfVar10[3] +
                         (fVar28 * auVar27._12_4_ + fVar24 * fVar20 + fVar22 * fVar18) * fVar19;
            uVar11 = uVar11 + 1;
            pfVar10 = pfVar10 + 4;
          } while (uVar11 < in_stack_00000024);
        }
        in_stack_0000002c = in_stack_0000002c + 1;
        fVar19 = *in_stack_0000002c;
      }
      if (in_stack_00000030 == 0) {
        *in_stack_00000010 = CONCAT44(fVar32,fVar30);
        *local_4b0 = fVar16;
        if (in_stack_00000024 != 0) {
          pauVar8 = (undefined1 (*) [16])local_420;
          piVar9 = in_stack_00000020;
          uVar11 = in_stack_00000024;
          do {
            puVar5 = (undefined8 *)*piVar9;
            auVar27 = *pauVar8;
            *puVar5 = auVar27._0_8_;
            *(int *)(puVar5 + 1) = auVar27._8_4_;
            *piVar9 = *piVar9 + in_stack_00000018;
            piVar1 = (int *)((int)piVar9 + ((int)in_stack_0000001c - (int)in_stack_00000020));
            *piVar1 = *piVar1 + in_stack_00000018;
            pauVar8 = pauVar8 + 1;
            piVar9 = piVar9 + 1;
            uVar11 = uVar11 - 1;
          } while (uVar11 != 0);
        }
        puVar13 = local_4a8;
        puVar15 = local_4ac;
        for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
          *puVar15 = *puVar13;
          puVar13 = puVar13 + 1;
          puVar15 = puVar15 + 1;
        }
        for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
          *(undefined1 *)puVar15 = *(undefined1 *)puVar13;
          puVar13 = (undefined4 *)((int)puVar13 + 1);
          puVar15 = (undefined4 *)((int)puVar15 + 1);
        }
      }
      else {
        puVar13 = local_4a8;
        puVar15 = local_4ac;
        for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
          *puVar15 = *puVar13;
          puVar13 = puVar13 + 1;
          puVar15 = puVar15 + 1;
        }
        for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
          *(undefined1 *)puVar15 = *(undefined1 *)puVar13;
          puVar13 = (undefined4 *)((int)puVar13 + 1);
          puVar15 = (undefined4 *)((int)puVar15 + 1);
        }
        *in_stack_00000010 = CONCAT44(fVar32,fVar30);
        *local_4b0 = fVar16;
        if (in_stack_00000024 != 0) {
          pauVar8 = (undefined1 (*) [16])local_420;
          piVar9 = in_stack_00000020;
          uVar11 = in_stack_00000024;
          do {
            puVar5 = (undefined8 *)*piVar9;
            auVar27 = *pauVar8;
            *puVar5 = auVar27._0_8_;
            *(int *)(puVar5 + 1) = auVar27._8_4_;
            *piVar9 = *piVar9 + in_stack_00000018;
            piVar1 = (int *)(((int)in_stack_0000001c - (int)in_stack_00000020) + (int)piVar9);
            *piVar1 = *piVar1 + in_stack_00000018;
            pauVar8 = pauVar8 + 1;
            piVar9 = piVar9 + 1;
            uVar11 = uVar11 - 1;
          } while (uVar11 != 0);
        }
      }
      local_4ac = (undefined4 *)((int)local_4ac + in_stack_00000018);
      local_4a8 = (undefined4 *)((int)local_4a8 + in_stack_00000018);
      in_stack_00000010 = (undefined8 *)((int)in_stack_00000010 + in_stack_00000018);
      local_4b0 = (float *)((int)local_4b0 + in_stack_00000018);
      in_stack_0000002c = in_stack_0000002c + 1;
      in_stack_0000000c = (float *)((int)in_stack_0000000c + in_stack_00000018);
      local_4a4 = local_4a4 + -1;
    } while (local_4a4 != 0);
  }
  return (int)in_stack_0000000c;
}
