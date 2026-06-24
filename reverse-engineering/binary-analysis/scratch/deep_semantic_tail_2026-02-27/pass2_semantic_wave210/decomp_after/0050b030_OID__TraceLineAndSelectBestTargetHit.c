/* address: 0x0050b030 */
/* name: OID__TraceLineAndSelectBestTargetHit */
/* signature: int OID__TraceLineAndSelectBestTargetHit(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int OID__TraceLineAndSelectBestTargetHit(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int *piVar8;
  int unaff_EDI;
  undefined4 *puVar9;
  float10 fVar10;
  float in_stack_00000018;
  float in_stack_0000001c;
  float in_stack_00000020;
  undefined4 in_stack_00000024;
  undefined4 in_stack_00000028;
  undefined4 in_stack_0000002c;
  undefined4 in_stack_00000030;
  undefined4 in_stack_00000034;
  int *in_stack_00000038;
  undefined4 *in_stack_0000003c;
  int in_stack_00000040;
  int in_stack_00000044;
  int in_stack_00000048;
  uint in_stack_0000004c;
  void *in_stack_00000050;
  uint in_stack_00000054;
  float fStack_1a0;
  float local_19c;
  float local_198;
  undefined4 local_194;
  undefined4 uStack_170;
  float local_14c;
  float local_148;
  float local_144;
  undefined1 auStack_13c [16];
  float fStack_12c;
  float fStack_128;
  float fStack_124;
  undefined4 uStack_11c;
  undefined1 auStack_118 [16];
  undefined4 uStack_108;
  undefined4 uStack_104;
  undefined4 uStack_100;
  undefined4 uStack_f8;
  undefined4 local_f4 [2];
  undefined1 local_ec [96];
  undefined4 uStack_8c;
  undefined4 local_74;
  float fStack_70;
  float fStack_6c;
  float fStack_68;
  undefined4 local_4c;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puVar9 = in_stack_0000003c;
  puStack_8 = &LAB_005d5bb8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  in_stack_0000003c[2] = 0;
  local_f4[0] = 0;
  vector_constructor_iterator_nothrow(local_ec,0x10,6,&LAB_00402d20);
  local_74 = 0;
  local_4c = 0;
  local_2c = 0;
  local_28 = 0;
  local_24 = 0;
  local_194 = 0xffffffff;
  local_19c = 99999.0;
  iVar4 = CStaticShadows__Helper_00490a40
                    (&DAT_006fadc8,(int)&stack0x00000004,(int)&local_14c,in_stack_00000050,unaff_EDI
                    );
  if (iVar4 != 0) {
    puVar9[2] = 1;
    local_19c = SQRT((in_stack_00000018 - local_14c) * (in_stack_00000018 - local_14c) +
                     (in_stack_0000001c - local_148) * (in_stack_0000001c - local_148) +
                     (in_stack_00000020 - local_144) * (in_stack_00000020 - local_144));
    puVar9[3] = local_19c;
  }
  local_198 = local_19c;
  piVar8 = (int *)0x0;
  iVar5 = CMapWho__GetFirstEntryWithinLine
                    (in_stack_00000018,in_stack_0000001c,in_stack_00000020,in_stack_00000024,
                     in_stack_00000028,in_stack_0000002c,in_stack_00000030,in_stack_00000034);
  if (iVar5 != 0) {
    do {
      piVar6 = (int *)CMapWhoEntry__GetOwner();
      if ((((piVar6 == in_stack_00000038) || ((*(byte *)(piVar6 + 0xb) & 0x10) != 0)) ||
          ((in_stack_0000004c & piVar6[0xd]) != 0)) ||
         ((((in_stack_00000054 & piVar6[0xd]) == 0 ||
           (piVar7 = (int *)CCollisionSeekingRound__Helper_004f3d10((int)piVar6),
           puVar9 = in_stack_0000003c, piVar7 == (int *)0x0)) ||
          ((*(byte *)(piVar7 + 3) & 0xc0) == 0)))) {
LAB_0050b4bc:
        iVar5 = CMapWho__GetNextEntryWithinLine();
      }
      else {
        if (((*(byte *)(piVar6 + 0xb) & 4) == 0) || ((piVar6[0xd] & 0x100U) != 0)) {
          iVar5 = (**(code **)(*piVar7 + 0x1c))();
          fVar1 = *(float *)(iVar5 + 4) + (float)piVar6[7];
          fVar2 = *(float *)(iVar5 + 8) + (float)piVar6[8];
          fVar3 = *(float *)(iVar5 + 0xc) + (float)piVar6[9];
          (**(code **)(*piVar7 + 0x1c))(&stack0x00000004,-fVar1,-fVar2,-fVar3,uStack_170,local_f4);
          iVar5 = CWorld__Helper_004780f0();
          puVar9 = in_stack_0000003c;
          if (iVar5 != 0) {
            fVar1 = fVar1 - in_stack_00000018;
            fVar2 = fVar2 - in_stack_0000001c;
            fVar3 = fVar3 - in_stack_00000020;
            fVar10 = (float10)(**(code **)(*piVar6 + 0x44))();
            fStack_1a0 = (float)((float10)SQRT(fVar1 * fVar1 + fVar2 * fVar2 + fVar3 * fVar3) -
                                fVar10);
            puVar9 = in_stack_0000003c;
            if (((iVar4 == 0) || (fStack_1a0 < local_19c)) &&
               ((piVar8 == (int *)0x0 || (fStack_1a0 < local_198)))) {
              uStack_8c = 0xffffffff;
              if (((in_stack_00000048 == 2) ||
                  ((((byte)piVar7[3] & 0xc) == 8 && (in_stack_00000044 == 1)))) &&
                 (piVar7 = (int *)piVar7[6], piVar7 != (int *)0x0)) {
                fStack_12c = (float)piVar6[7] + (float)piVar7[1];
                uStack_11c = 0;
                fStack_128 = (float)piVar7[2] + (float)piVar6[8];
                uStack_f8 = 0;
                fStack_124 = (float)piVar7[3] + (float)piVar6[9];
                uStack_104 = 0;
                uStack_108 = 0;
                uStack_100 = 0;
                iVar5 = (**(code **)(*piVar7 + 0x10))
                                  (auStack_13c,auStack_118,&stack0x00000004,local_f4);
                puVar9 = in_stack_0000003c;
                if ((iVar5 == 0) ||
                   (((fStack_1a0 = SQRT((fStack_70 - in_stack_00000018) *
                                        (fStack_70 - in_stack_00000018) +
                                        (fStack_6c - in_stack_0000001c) *
                                        (fStack_6c - in_stack_0000001c) +
                                        (fStack_68 - in_stack_00000020) *
                                        (fStack_68 - in_stack_00000020)), iVar4 != 0 &&
                     (local_19c < fStack_1a0)) || (local_198 < fStack_1a0)))) goto LAB_0050b4bc;
              }
              if (in_stack_00000040 != 0) {
                in_stack_0000003c[2] = 3;
                ExceptionList = local_c;
                return 3;
              }
              local_194 = uStack_8c;
              local_198 = fStack_1a0;
              piVar8 = piVar6;
              puVar9 = in_stack_0000003c;
            }
          }
          goto LAB_0050b4bc;
        }
        iVar5 = CMapWho__GetNextEntryWithinLine();
        puVar9 = in_stack_0000003c;
      }
    } while (iVar5 != 0);
    if (piVar8 != (int *)0x0) {
      *puVar9 = piVar8;
      puVar9[1] = local_194;
      puVar9[2] = 3;
      puVar9[3] = local_198;
    }
  }
  ExceptionList = local_c;
  return puVar9[2];
}
