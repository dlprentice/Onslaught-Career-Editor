/* address: 0x0050b9c0 */
/* name: CWorld__LoadWorld */
/* signature: bool __thiscall CWorld__LoadWorld(void * this, void * levelName) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool __thiscall CWorld__LoadWorld(void *this,void *levelName)

{
  byte bVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  short sVar4;
  ushort uVar5;
  int *piVar6;
  byte *pbVar7;
  int iVar8;
  undefined4 uVar9;
  void *pvVar10;
  int *piVar11;
  undefined4 *puVar12;
  undefined3 extraout_var;
  undefined3 extraout_var_00;
  undefined4 *puVar13;
  int extraout_ECX;
  int iVar14;
  uint uVar15;
  uint uVar16;
  char cVar17;
  byte *pbVar18;
  char *pcVar19;
  int unaff_EDI;
  char *pcVar20;
  char *pcVar21;
  bool bVar22;
  int unaff_retaddr;
  int *in_stack_00000008;
  char in_stack_0000000f;
  char *in_stack_00000010;
  char *in_stack_00000014;
  char cStack00000018;
  int iStack0000001c;
  short sStack00000020;
  short sStack00000024;
  uint in_stack_00000028;
  int in_stack_0000002c;
  int iStack00000030;
  float fStack00000034;
  float in_stack_00000038;
  undefined4 in_stack_0000003c;
  undefined4 in_stack_00000040;
  undefined4 uStack00000048;
  undefined4 in_stack_0000004c;
  undefined4 in_stack_00000050;
  float in_stack_00000054;
  undefined4 in_stack_00000058;
  float in_stack_0000005c;
  undefined4 in_stack_00000060;
  undefined4 in_stack_00000064;
  undefined4 in_stack_00000068;
  undefined4 uStack0000006c;
  undefined4 in_stack_00000070;
  undefined4 in_stack_00000074;
  undefined4 uStack00000078;
  undefined4 uStack0000007c;
  undefined4 uStack00000080;
  undefined **in_stack_00000090;
  float in_stack_00000094;
  float in_stack_00000098;
  void *in_stack_000038c0;
  int in_stack_000038d4;
  int in_stack_000038d8;
  undefined4 uStack_c;
  undefined1 *puStack_8;
  uint uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d5c95;
  uStack_c = ExceptionList;
  ExceptionList = &uStack_c;
  CRT__AllocaProbe();
  iStack0000001c = -1;
  uStack00000078 = 1;
  uStack00000080 = 1;
  uStack00000048 = 0x3f000000;
  uStack0000007c = 0x3f000000;
  uStack0000006c = 0;
  fStack00000034 = -NAN;
  iStack00000030 = extraout_ECX;
  if (in_stack_000038d8 != 0) {
    if (DAT_0067a748 != (int *)0x0) {
      (**(code **)(*DAT_0067a748 + 4))();
      DAT_0067a748 = (int *)0x0;
    }
    if (DAT_0067a07c != (void *)0x0) {
      OID__FreeObject(DAT_0067a07c);
      DAT_0067a07c = (void *)0x0;
    }
    if (DAT_0067a078 != (void *)0x0) {
      OID__FreeObject(DAT_0067a078);
      DAT_0067a078 = (void *)0x0;
    }
    CWorld__InitLODLists();
  }
  puVar13 = (undefined4 *)&stack0x00002920;
  for (iVar14 = 1000; iVar14 != 0; iVar14 = iVar14 + -1) {
    *puVar13 = 0xffffffff;
    puVar13 = puVar13 + 1;
  }
  puVar13 = (undefined4 *)&stack0x00001980;
  for (iVar14 = 1000; iVar14 != 0; iVar14 = iVar14 + -1) {
    *puVar13 = 0;
    puVar13 = puVar13 + 1;
  }
  puVar13 = (undefined4 *)&stack0x000009e0;
  for (iVar14 = 1000; iVar14 != 0; iVar14 = iVar14 + -1) {
    *puVar13 = 0;
    puVar13 = puVar13 + 1;
  }
  puStack_8 = (undefined1 *)0x0;
  DXMemBuffer__ReadBytes();
  if (((uStack_4 & 0xffff) < 0x2b) || (0x32 < (uStack_4 & 0xffff))) {
    bVar22 = false;
  }
  else {
    CWorld__LoadWorldHeader();
    if (in_stack_000038d8 != 0) {
      if (DAT_0067a748 == (int *)0x0) {
        in_stack_00000008 = (int *)OID__AllocObject();
        if (in_stack_00000008 == (int *)0x0) {
          DAT_0067a748 = (int *)0x0;
        }
        else {
          in_stack_00000008[1] = 0;
          *in_stack_00000008 = (int)&PTR_CFrontEndPage__ActiveNotification_NoOp_005d92d4;
          CSPtrSet__Init(in_stack_00000008 + 2);
          CSPtrSet__Init(in_stack_00000008 + 6);
          *in_stack_00000008 = (int)&PTR_LAB_005dfcb4;
          DAT_0067a748 = in_stack_00000008;
        }
      }
      if (DAT_0067a07c == (void *)0x0) {
        DAT_0067a07c = (void *)OID__AllocObject();
      }
      if (DAT_0067a078 == (void *)0x0) {
        DAT_0067a078 = (void *)OID__AllocObject();
      }
    }
    DXMemBuffer__ReadBytes();
    CWorld__LoadScriptEvents();
    if ((in_stack_000038d4 == 0) && (iStack0000001c != -1)) {
      CWorld__LoadWorldFile();
    }
    DXMemBuffer__ReadBytes();
    if ((in_stack_000038d4 == 0) && (iStack0000001c != -1)) {
      iVar14 = 0;
    }
    else {
      iVar14 = 1;
    }
    CWorld__CanLoadMapSection(&DAT_006fadc8,(int)fStack00000034,iVar14,1,unaff_EDI);
    CWorld__LoadNamedMeshCacheFromBuffer(0x89c9a0);
    DXMemBuffer__ReadBytes();
    CConsole__Status(&DAT_00663498,s_Loading_units_0063d450);
    while (sStack00000024 != 0) {
      DXMemBuffer__ReadBytes();
      if ((unaff_retaddr == 8) || (unaff_retaddr == 0x19)) {
        CInfluenceMap__Init();
        in_stack_00000090 = &PTR_LAB_005dc1c0;
        sVar4 = (short)uStack_4;
        if (sVar4 < 0x11) {
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
LAB_0050c8ae:
          DXMemBuffer__ReadBytes();
        }
        else if (sVar4 < 0x14) {
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000013c)[cVar17] != '\0');
        }
        else if (sVar4 < 0x1c) {
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000013c)[cVar17] != '\0');
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000023c)[cVar17] != '\0');
        }
        else {
          if (0x21 < sVar4) {
            if (sVar4 < 0x2e) {
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000013c)[cVar17] != '\0');
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000023c)[cVar17] != '\0');
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000033c)[cVar17] != '\0');
            }
            else {
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              DXMemBuffer__ReadBytes();
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000013c)[cVar17] != '\0');
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000023c)[cVar17] != '\0');
              cVar17 = -1;
              do {
                cVar17 = cVar17 + '\x01';
                DXMemBuffer__ReadBytes();
              } while ((&stack0x0000033c)[cVar17] != '\0');
              DXMemBuffer__ReadBytes();
            }
            goto LAB_0050c8ae;
          }
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000013c)[cVar17] != '\0');
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000023c)[cVar17] != '\0');
          cVar17 = -1;
          do {
            cVar17 = cVar17 + '\x01';
            DXMemBuffer__ReadBytes();
          } while ((&stack0x0000033c)[cVar17] != '\0');
        }
        DXMemBuffer__ReadBytes();
        DXMemBuffer__ReadBytes();
        (&stack0x00000650)[uStack_c._3_1_] = 0;
        DXMemBuffer__ReadBytes();
        if (&stack0x00000000 != (undefined1 *)0xfffff9b0) {
          piVar6 = (int *)*DAT_008553fc;
          DAT_008553fc[2] = (int)piVar6;
          if (piVar6 == (int *)0x0) {
            iVar14 = 0;
          }
          else {
            iVar14 = *piVar6;
          }
          while (iVar14 != 0) {
            pbVar18 = *(byte **)(iVar14 + 0xb0);
            pbVar7 = &stack0x00000650;
            do {
              bVar1 = *pbVar7;
              bVar22 = bVar1 < *pbVar18;
              if (bVar1 != *pbVar18) {
LAB_0050c955:
                iVar8 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                goto LAB_0050c95a;
              }
              if (bVar1 == 0) break;
              bVar1 = pbVar7[1];
              bVar22 = bVar1 < pbVar18[1];
              if (bVar1 != pbVar18[1]) goto LAB_0050c955;
              pbVar7 = pbVar7 + 2;
              pbVar18 = pbVar18 + 2;
            } while (bVar1 != 0);
            iVar8 = 0;
LAB_0050c95a:
            if (iVar8 == 0) goto LAB_0050c983;
            piVar6 = *(int **)(DAT_008553fc[2] + 4);
            DAT_008553fc[2] = (int)piVar6;
            if (piVar6 == (int *)0x0) {
              iVar14 = 0;
            }
            else {
              iVar14 = *piVar6;
            }
          }
        }
        iVar14 = 0;
LAB_0050c983:
        puVar3 = puStack_8;
        if (iVar14 != 0) {
          iVar14 = CWorldPhysicsManager__CreateSquad();
          if (iVar14 == 0) {
            if (&stack0x00000000 != (undefined1 *)0xfffff9b0) {
              pvVar10 = CSPtrSet__First(DAT_008553fc);
              while (pvVar10 != (void *)0x0) {
                pbVar18 = *(byte **)((int)pvVar10 + 0xb0);
                pbVar7 = &stack0x00000650;
                do {
                  bVar1 = *pbVar7;
                  bVar22 = bVar1 < *pbVar18;
                  if (bVar1 != *pbVar18) {
LAB_0050ca77:
                    iVar14 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                    goto LAB_0050ca7c;
                  }
                  if (bVar1 == 0) break;
                  bVar1 = pbVar7[1];
                  bVar22 = bVar1 < pbVar18[1];
                  if (bVar1 != pbVar18[1]) goto LAB_0050ca77;
                  pbVar7 = pbVar7 + 2;
                  pbVar18 = pbVar18 + 2;
                } while (bVar1 != 0);
                iVar14 = 0;
LAB_0050ca7c:
                if (iVar14 == 0) break;
                pvVar10 = CSPtrSet__Next(DAT_008553fc);
              }
            }
            uVar9 = CWorldPhysicsManager__CreateThingByType();
            puVar3 = puStack_8;
            *(undefined4 *)(&stack0x000009e0 + (int)puStack_8 * 4) = uVar9;
            puVar12 = (undefined4 *)InitThing__CreateThingByType();
            puVar13 = (undefined4 *)*puVar12;
            *(undefined4 **)(&stack0x00001980 + (int)puVar3 * 4) = puVar12;
            (*(code *)*puVar13)();
          }
          else {
            puVar12 = (undefined4 *)InitThing__CreateThingByType();
            puVar3 = puStack_8;
            puVar13 = (undefined4 *)*puVar12;
            *(undefined4 **)(&stack0x00001980 + (int)puStack_8 * 4) = puVar12;
            (*(code *)*puVar13)();
            uVar15 = 0xffffffff;
            in_stack_00000010 = (char *)(puVar12 + 0xf0);
            *(int *)(&stack0x000009e0 + (int)puVar3 * 4) = iVar14;
            pcVar19 = &stack0x00000650;
            do {
              pcVar21 = pcVar19;
              if (uVar15 == 0) break;
              uVar15 = uVar15 - 1;
              pcVar21 = pcVar19 + 1;
              cVar17 = *pcVar19;
              pcVar19 = pcVar21;
            } while (cVar17 != '\0');
            uVar15 = ~uVar15;
            pcVar19 = pcVar21 + -uVar15;
            pcVar21 = in_stack_00000010;
            for (uVar16 = uVar15 >> 2; uVar16 != 0; uVar16 = uVar16 - 1) {
              *(undefined4 *)pcVar21 = *(undefined4 *)pcVar19;
              pcVar19 = pcVar19 + 4;
              pcVar21 = pcVar21 + 4;
            }
            for (uVar15 = uVar15 & 3; uVar15 != 0; uVar15 = uVar15 - 1) {
              *pcVar21 = *pcVar19;
              pcVar19 = pcVar19 + 1;
              pcVar21 = pcVar21 + 1;
            }
            puVar12[0xef] = 1;
            *(undefined4 *)(*(int *)(&stack0x000009e0 + (int)puVar3 * 4) + 0x84) = 1;
          }
          CWorldMeshList__Add();
LAB_0050cad9:
          puVar3 = (undefined1 *)((int)puStack_8 + 1);
        }
      }
      else if (unaff_retaddr == 0x1c) {
        piVar6 = (int *)InitThing__CreateThingByType();
        in_stack_00000010 = &stack0x00001980 + (int)puStack_8 * 4;
        *(int **)in_stack_00000010 = piVar6;
        puVar3 = puStack_8;
        if (piVar6 != (int *)0x0) {
          (**(code **)(*piVar6 + 4))();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          puVar3 = puStack_8;
          *(undefined1 *)(in_stack_0000000f + 0x3c0 + (int)piVar6) = 0;
          if (piVar6 != (int *)0xfffffc40) {
            piVar11 = (int *)*DAT_008553fc;
            DAT_008553fc[2] = (int)piVar11;
            if (piVar11 == (int *)0x0) {
              iVar14 = 0;
            }
            else {
              iVar14 = *piVar11;
            }
            while (iVar14 != 0) {
              pbVar18 = *(byte **)(iVar14 + 0xb0);
              pbVar7 = (byte *)(piVar6 + 0xf0);
              do {
                bVar1 = *pbVar7;
                bVar22 = bVar1 < *pbVar18;
                if (bVar1 != *pbVar18) {
LAB_0050bd40:
                  iVar8 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                  goto LAB_0050bd45;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar7[1];
                bVar22 = bVar1 < pbVar18[1];
                if (bVar1 != pbVar18[1]) goto LAB_0050bd40;
                pbVar7 = pbVar7 + 2;
                pbVar18 = pbVar18 + 2;
              } while (bVar1 != 0);
              iVar8 = 0;
LAB_0050bd45:
              if (iVar8 == 0) goto LAB_0050bd6a;
              piVar11 = *(int **)(DAT_008553fc[2] + 4);
              DAT_008553fc[2] = (int)piVar11;
              if (piVar11 == (int *)0x0) {
                iVar14 = 0;
              }
              else {
                iVar14 = *piVar11;
              }
            }
          }
          iVar14 = 0;
LAB_0050bd6a:
          DXMemBuffer__ReadBytes();
          if (iVar14 != 0) {
            uVar9 = CWorldPhysicsManager__CreateSquad();
            *(undefined4 *)(&stack0x000009e0 + (int)puVar3 * 4) = uVar9;
          }
          if (*(int *)(&stack0x000009e0 + (int)puVar3 * 4) == 0) {
            OID__FreeObject(piVar6);
            in_stack_00000010[0] = '\0';
            in_stack_00000010[1] = '\0';
            in_stack_00000010[2] = '\0';
            in_stack_00000010[3] = '\0';
            puVar3 = puStack_8;
          }
          else {
            puVar3 = (undefined1 *)((int)puVar3 + 1);
          }
        }
      }
      else if (unaff_retaddr == 0x23) {
        piVar6 = (int *)InitThing__CreateThingByType();
        in_stack_00000010 = &stack0x00001980 + (int)puStack_8 * 4;
        *(int **)in_stack_00000010 = piVar6;
        puVar3 = puStack_8;
        if (piVar6 != (int *)0x0) {
          (**(code **)(*piVar6 + 4))();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          (&stack0x00000750)[levelName._3_1_] = 0;
          if (0x27 < (ushort)uStack_4) {
            DXMemBuffer__ReadBytes();
          }
          if (&stack0x00000000 != (undefined1 *)0xfffff8b0) {
            piVar11 = (int *)*DAT_00855404;
            DAT_00855404[2] = (int)piVar11;
            if (piVar11 == (int *)0x0) {
              iVar14 = 0;
            }
            else {
              iVar14 = *piVar11;
            }
            while (iVar14 != 0) {
              pbVar18 = *(byte **)(iVar14 + 0x20);
              pbVar7 = &stack0x00000750;
              do {
                bVar1 = *pbVar7;
                bVar22 = bVar1 < *pbVar18;
                if (bVar1 != *pbVar18) {
LAB_0050bea9:
                  iVar8 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                  goto LAB_0050beae;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar7[1];
                bVar22 = bVar1 < pbVar18[1];
                if (bVar1 != pbVar18[1]) goto LAB_0050bea9;
                pbVar7 = pbVar7 + 2;
                pbVar18 = pbVar18 + 2;
              } while (bVar1 != 0);
              iVar8 = 0;
LAB_0050beae:
              if (iVar8 == 0) goto LAB_0050bed3;
              piVar11 = *(int **)(DAT_00855404[2] + 4);
              DAT_00855404[2] = (int)piVar11;
              if (piVar11 == (int *)0x0) {
                iVar14 = 0;
              }
              else {
                iVar14 = *piVar11;
              }
            }
          }
          iVar14 = 0;
LAB_0050bed3:
          piVar6[0xef] = iVar14;
          if (&stack0x00000000 != (undefined1 *)0xfffff8b0) {
            pvVar10 = CSPtrSet__First(DAT_00855404);
            while (pvVar10 != (void *)0x0) {
              pbVar18 = *(byte **)((int)pvVar10 + 0x20);
              pbVar7 = &stack0x00000750;
              do {
                bVar1 = *pbVar7;
                bVar22 = bVar1 < *pbVar18;
                if (bVar1 != *pbVar18) {
LAB_0050bf27:
                  iVar14 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                  goto LAB_0050bf2c;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar7[1];
                bVar22 = bVar1 < pbVar18[1];
                if (bVar1 != pbVar18[1]) goto LAB_0050bf27;
                pbVar7 = pbVar7 + 2;
                pbVar18 = pbVar18 + 2;
              } while (bVar1 != 0);
              iVar14 = 0;
LAB_0050bf2c:
              if (iVar14 == 0) break;
              piVar11 = *(int **)(DAT_00855404[2] + 4);
              DAT_00855404[2] = (int)piVar11;
              if (piVar11 == (int *)0x0) {
                pvVar10 = (void *)0x0;
              }
              else {
                pvVar10 = (void *)*piVar11;
              }
            }
          }
          iVar14 = CWorldPhysicsManager__CreateEffect();
          *(int *)(&stack0x000009e0 + (int)puStack_8 * 4) = iVar14;
          if (iVar14 != 0) goto LAB_0050cad9;
          sprintf(&stack0x00000850,s____Unable_to_find_thing_in_physi_0063d428);
          DebugTrace(&stack0x00000850);
          OID__FreeObject(piVar6);
          in_stack_00000010[0] = '\0';
          in_stack_00000010[1] = '\0';
          in_stack_00000010[2] = '\0';
          in_stack_00000010[3] = '\0';
          puVar3 = puStack_8;
        }
      }
      else if (unaff_retaddr == 0x27) {
        piVar6 = (int *)InitThing__CreateThingByType();
        in_stack_00000010 = &stack0x00001980 + (int)puStack_8 * 4;
        *(int **)in_stack_00000010 = piVar6;
        puVar3 = puStack_8;
        if (piVar6 != (int *)0x0) {
          (**(code **)(*piVar6 + 4))();
          DXMemBuffer__ReadBytes();
          DXMemBuffer__ReadBytes();
          (&stack0x00000550)[cStack00000018] = 0;
          if (0x27 < (ushort)uStack_4) {
            DXMemBuffer__ReadBytes();
          }
          if (&stack0x00000000 != (undefined1 *)0xfffffab0) {
            piVar11 = (int *)*DAT_00855408;
            DAT_00855408[2] = (int)piVar11;
            if (piVar11 == (int *)0x0) {
              iVar14 = 0;
            }
            else {
              iVar14 = *piVar11;
            }
            while (iVar14 != 0) {
              pbVar18 = *(byte **)(iVar14 + 0x10);
              pbVar7 = &stack0x00000550;
              do {
                bVar1 = *pbVar7;
                bVar22 = bVar1 < *pbVar18;
                if (bVar1 != *pbVar18) {
LAB_0050c099:
                  iVar8 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                  goto LAB_0050c09e;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar7[1];
                bVar22 = bVar1 < pbVar18[1];
                if (bVar1 != pbVar18[1]) goto LAB_0050c099;
                pbVar7 = pbVar7 + 2;
                pbVar18 = pbVar18 + 2;
              } while (bVar1 != 0);
              iVar8 = 0;
LAB_0050c09e:
              if (iVar8 == 0) goto LAB_0050c0c3;
              piVar11 = *(int **)(DAT_00855408[2] + 4);
              DAT_00855408[2] = (int)piVar11;
              if (piVar11 == (int *)0x0) {
                iVar14 = 0;
              }
              else {
                iVar14 = *piVar11;
              }
            }
          }
          iVar14 = 0;
LAB_0050c0c3:
          piVar6[0xef] = iVar14;
          if (&stack0x00000000 != (undefined1 *)0xfffffab0) {
            pvVar10 = CSPtrSet__First(DAT_00855408);
            while (pvVar10 != (void *)0x0) {
              pbVar18 = *(byte **)((int)pvVar10 + 0x10);
              pbVar7 = &stack0x00000550;
              do {
                bVar1 = *pbVar7;
                bVar22 = bVar1 < *pbVar18;
                if (bVar1 != *pbVar18) {
LAB_0050c117:
                  iVar14 = (1 - (uint)bVar22) - (uint)(bVar22 != 0);
                  goto LAB_0050c11c;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar7[1];
                bVar22 = bVar1 < pbVar18[1];
                if (bVar1 != pbVar18[1]) goto LAB_0050c117;
                pbVar7 = pbVar7 + 2;
                pbVar18 = pbVar18 + 2;
              } while (bVar1 != 0);
              iVar14 = 0;
LAB_0050c11c:
              if (iVar14 == 0) break;
              piVar11 = *(int **)(DAT_00855408[2] + 4);
              DAT_00855408[2] = (int)piVar11;
              if (piVar11 == (int *)0x0) {
                pvVar10 = (void *)0x0;
              }
              else {
                pvVar10 = (void *)*piVar11;
              }
            }
          }
          iVar14 = CWorldPhysicsManager__CreateTrigger();
          *(int *)(&stack0x000009e0 + (int)puStack_8 * 4) = iVar14;
          if (iVar14 != 0) goto LAB_0050cad9;
          sprintf(&stack0x00000918,s____Unable_to_find_thing_in_physi_0063d428);
          DebugTrace(&stack0x00000918);
          OID__FreeObject(piVar6);
          in_stack_00000010[0] = '\0';
          in_stack_00000010[1] = '\0';
          in_stack_00000010[2] = '\0';
          in_stack_00000010[3] = '\0';
          puVar3 = puStack_8;
        }
      }
      else if (unaff_retaddr == 0xf) {
        iVar14 = OID__CreateObject();
        piVar6 = (int *)(&stack0x000009e0 + (int)puStack_8 * 4);
        *piVar6 = iVar14;
        puVar3 = puStack_8;
        if (iVar14 != 0) {
          piVar11 = (int *)InitThing__CreateThingByType();
          *(int **)(&stack0x00001980 + (int)puStack_8 * 4) = piVar11;
          if (piVar11 == (int *)0x0) goto LAB_0050c263;
          (**(code **)(*piVar11 + 4))();
          puVar2 = puStack_8;
          puVar3 = (undefined1 *)((int)puStack_8 + 1);
          if (in_stack_000038d4 != 0) {
            iVar14 = (int)puStack_8 * 4;
            if (*(int **)(&stack0x000009e0 + (int)puStack_8 * 4) != (int *)0x0) {
              (**(code **)(**(int **)(&stack0x000009e0 + (int)puStack_8 * 4) + 4))();
            }
            OID__FreeObject(*(void **)(&stack0x00001980 + (int)puVar2 * 4));
            *(undefined4 *)(&stack0x000009e0 + iVar14) = 0;
            *(undefined4 *)(&stack0x00001980 + (int)puVar2 * 4) = 0;
            puVar3 = puStack_8;
          }
        }
      }
      else {
        iVar14 = OID__CreateObject();
        piVar6 = (int *)(&stack0x000009e0 + (int)puStack_8 * 4);
        *piVar6 = iVar14;
        puVar3 = puStack_8;
        if (iVar14 != 0) {
          piVar11 = (int *)InitThing__CreateThingByType();
          *(int **)(&stack0x00001980 + (int)puStack_8 * 4) = piVar11;
          if (piVar11 != (int *)0x0) {
            (**(code **)(*piVar11 + 4))();
            goto LAB_0050cad9;
          }
LAB_0050c263:
          puVar3 = puStack_8;
          if ((int *)*piVar6 != (int *)0x0) {
            (**(code **)(*(int *)*piVar6 + 4))();
            puVar3 = puStack_8;
          }
        }
      }
      puStack_8 = puVar3;
      _sStack00000024 = _sStack00000024 + 0xffff;
    }
    CConsole__StatusDone(&DAT_00663498,s_Loading_units_0063d450,'\x01');
    CConsole__Status(&DAT_00663498,s_Loading_trees_0063d418);
    DXMemBuffer__ReadBytes();
    while (sStack00000020 != 0) {
      in_stack_00000010 = (char *)0x0;
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      CInfluenceMap__Init();
      uVar15 = 0xffffffff;
      pcVar19 = s_DefaultTree0_0062d7a0;
      do {
        pcVar21 = pcVar19;
        if (uVar15 == 0) break;
        uVar15 = uVar15 - 1;
        pcVar21 = pcVar19 + 1;
        cVar17 = *pcVar19;
        pcVar19 = pcVar21;
      } while (cVar17 != '\0');
      uVar15 = ~uVar15;
      in_stack_00000090 = &PTR_LAB_005dc18c;
      pcVar19 = pcVar21 + -uVar15;
      pcVar21 = &stack0x00000450;
      for (uVar16 = uVar15 >> 2; uVar16 != 0; uVar16 = uVar16 - 1) {
        *(undefined4 *)pcVar21 = *(undefined4 *)pcVar19;
        pcVar19 = pcVar19 + 4;
        pcVar21 = pcVar21 + 4;
      }
      for (uVar15 = uVar15 & 3; uVar15 != 0; uVar15 = uVar15 - 1) {
        *pcVar21 = *pcVar19;
        pcVar19 = pcVar19 + 1;
        pcVar21 = pcVar21 + 1;
      }
      DXMemBuffer__ReadBytes();
      cVar17 = '\0';
      if ('\0' < uStack_c._3_1_) {
        do {
          DXMemBuffer__ReadBytes();
          cVar17 = cVar17 + '\x01';
        } while (cVar17 < uStack_c._3_1_);
      }
      (&stack0x00000450)[cVar17] = 0;
      DXMemBuffer__ReadBytes();
      if ((in_stack_000038d4 != 0) || (iStack0000001c == -1)) {
        RandomSeedPair__Set(&stack0x00000038,0);
        for (; unaff_retaddr != 0; unaff_retaddr = unaff_retaddr + -1) {
          piVar6 = (int *)OID__CreateObject();
          in_stack_00000028 = Random__NextLCGAbs((int *)&stack0x00000038);
          in_stack_00000028 = in_stack_00000028 & 0x8000ffff;
          if ((int)in_stack_00000028 < 0) {
            in_stack_00000028 = (in_stack_00000028 - 1 | 0xffff0000) + 1;
          }
          in_stack_0000005c = (float)(int)in_stack_00000028 * _DAT_005d8d54;
          in_stack_00000028 = Random__NextLCGAbs((int *)&stack0x00000038);
          in_stack_00000028 = in_stack_00000028 & 0x8000ffff;
          if ((int)in_stack_00000028 < 0) {
            in_stack_00000028 = (in_stack_00000028 - 1 | 0xffff0000) + 1;
          }
          in_stack_00000094 =
               (in_stack_00000054 - _cStack00000018) * in_stack_0000005c + _cStack00000018;
          in_stack_00000098 =
               ((float)in_stack_00000008 - (float)in_stack_00000014) *
               (float)(int)in_stack_00000028 * _DAT_005d8d54 + (float)in_stack_00000014;
          (**(code **)(*piVar6 + 0x24))();
        }
      }
      _sStack00000020 = _sStack00000020 + -1;
    }
    DXMemBuffer__ReadBytes();
    for (; in_stack_0000002c != 0; in_stack_0000002c = in_stack_0000002c + -1) {
      CInfluenceMap__Init();
      uVar15 = 0xffffffff;
      pcVar19 = s_DefaultTree0_0062d7a0;
      do {
        pcVar21 = pcVar19;
        if (uVar15 == 0) break;
        uVar15 = uVar15 - 1;
        pcVar21 = pcVar19 + 1;
        cVar17 = *pcVar19;
        pcVar19 = pcVar21;
      } while (cVar17 != '\0');
      uVar15 = ~uVar15;
      in_stack_00000090 = &PTR_LAB_005dc18c;
      pcVar19 = pcVar21 + -uVar15;
      pcVar21 = &stack0x00000450;
      for (uVar16 = uVar15 >> 2; uVar16 != 0; uVar16 = uVar16 - 1) {
        *(undefined4 *)pcVar21 = *(undefined4 *)pcVar19;
        pcVar19 = pcVar19 + 4;
        pcVar21 = pcVar21 + 4;
      }
      for (uVar15 = uVar15 & 3; uVar15 != 0; uVar15 = uVar15 - 1) {
        *pcVar21 = *pcVar19;
        pcVar19 = pcVar19 + 1;
        pcVar21 = pcVar21 + 1;
      }
      DXMemBuffer__ReadBytes();
      cVar17 = '\0';
      if ('\0' < uStack_c._3_1_) {
        do {
          DXMemBuffer__ReadBytes();
          cVar17 = cVar17 + '\x01';
        } while (cVar17 < uStack_c._3_1_);
      }
      (&stack0x00000550)[cVar17] = 0;
      DXMemBuffer__ReadBytes();
      for (; unaff_retaddr != 0; unaff_retaddr = unaff_retaddr + -1) {
        DXMemBuffer__ReadBytes();
        DXMemBuffer__ReadBytes();
        DXMemBuffer__ReadBytes();
        if ((in_stack_000038d4 != 0) || (iStack0000001c == -1)) {
          uVar15 = 0xffffffff;
          pcVar19 = &stack0x00000550;
          do {
            pcVar21 = pcVar19;
            if (uVar15 == 0) break;
            uVar15 = uVar15 - 1;
            pcVar21 = pcVar19 + 1;
            cVar17 = *pcVar19;
            pcVar19 = pcVar21;
          } while (cVar17 != '\0');
          uVar15 = ~uVar15;
          pcVar19 = pcVar21 + -uVar15;
          pcVar21 = &stack0x00000450;
          for (uVar16 = uVar15 >> 2; uVar16 != 0; uVar16 = uVar16 - 1) {
            *(undefined4 *)pcVar21 = *(undefined4 *)pcVar19;
            pcVar19 = pcVar19 + 4;
            pcVar21 = pcVar21 + 4;
          }
          for (uVar15 = uVar15 & 3; uVar15 != 0; uVar15 = uVar15 - 1) {
            *pcVar21 = *pcVar19;
            pcVar19 = pcVar19 + 1;
            pcVar21 = pcVar21 + 1;
          }
          sprintf(&stack0x00000018,&DAT_006245cc);
          uVar15 = 0xffffffff;
          pcVar19 = &stack0x00000018;
          do {
            pcVar21 = pcVar19;
            if (uVar15 == 0) break;
            uVar15 = uVar15 - 1;
            pcVar21 = pcVar19 + 1;
            cVar17 = *pcVar19;
            pcVar19 = pcVar21;
          } while (cVar17 != '\0');
          uVar15 = ~uVar15;
          iVar14 = -1;
          pcVar19 = &stack0x00000450;
          do {
            pcVar20 = pcVar19;
            if (iVar14 == 0) break;
            iVar14 = iVar14 + -1;
            pcVar20 = pcVar19 + 1;
            cVar17 = *pcVar19;
            pcVar19 = pcVar20;
          } while (cVar17 != '\0');
          pcVar19 = pcVar21 + -uVar15;
          pcVar21 = pcVar20 + -1;
          for (uVar16 = uVar15 >> 2; uVar16 != 0; uVar16 = uVar16 - 1) {
            *(undefined4 *)pcVar21 = *(undefined4 *)pcVar19;
            pcVar19 = pcVar19 + 4;
            pcVar21 = pcVar21 + 4;
          }
          for (uVar15 = uVar15 & 3; uVar15 != 0; uVar15 = uVar15 - 1) {
            *pcVar21 = *pcVar19;
            pcVar19 = pcVar19 + 1;
            pcVar21 = pcVar21 + 1;
          }
          iVar14 = CMCBuggy__StrnICmpWithLocaleLock(&stack0x00000450,&DAT_00633a74,(void *)0x4);
          if ((iVar14 != 0) &&
             (iVar14 = CMCBuggy__StrnICmpWithLocaleLock(&stack0x00000450,&DAT_00633a6c,(void *)0x4),
             iVar14 != 0)) {
            piVar6 = (int *)OID__CreateObject();
            (**(code **)(*piVar6 + 0x24))();
          }
        }
      }
    }
    CConsole__StatusDone(&DAT_00663498,s_Loading_trees_0063d418,'\x01');
    if ((in_stack_000038d4 == 0) && (iStack0000001c != -1)) {
      CInfluenceMapManager__SkipLoad();
    }
    else {
      CInfluenceMapManager__Load();
    }
    in_stack_00000014 = (char *)0x0;
    if (0 < (int)puStack_8) {
      do {
        iVar14 = *(int *)(&stack0x00001980 + (int)in_stack_00000014 * 4);
        iVar8 = *(int *)(iVar14 + 0xa4);
        if ((iVar8 < 0) || ((int)puStack_8 <= iVar8)) {
          *(undefined4 *)(iVar14 + 0xa4) = 0;
        }
        else {
          *(undefined4 *)(iVar14 + 0xa4) = *(undefined4 *)(&stack0x000009e0 + iVar8 * 4);
        }
        if ((in_stack_000038d4 == 0) ||
           ((bVar22 = CCareer__DoesBaseThingExist(&CAREER,DAT_008a9ac8,(int)in_stack_00000014),
            CONCAT31(extraout_var,bVar22) != 0 &&
            ((*(int *)(&stack0x00002920 + (int)in_stack_00000014 * 4) == -1 ||
             (bVar22 = CCareer__IsWorldLater
                                 (&CAREER,DAT_008a9ac8,
                                  *(int *)(&stack0x00002920 + (int)in_stack_00000014 * 4)),
             CONCAT31(extraout_var_00,bVar22) == 0)))))) {
          (**(code **)(**(int **)(&stack0x000009e0 + (int)in_stack_00000014 * 4) + 0x24))();
          if (in_stack_000038d4 != 0) {
            puVar13 = (undefined4 *)OID__AllocObject();
            if (puVar13 == (undefined4 *)0x0) {
              puVar13 = (undefined4 *)0x0;
            }
            else {
              *puVar13 = 0;
            }
            CGenericActiveReader__SetReader
                      (puVar13,*(void **)(&stack0x000009e0 + (int)in_stack_00000014 * 4));
            CSPtrSet__AddToTail((void *)(iStack00000030 + 0xc0),puVar13);
          }
        }
        else {
          (**(code **)(**(int **)(&stack0x000009e0 + (int)in_stack_00000014 * 4) + 0x98))();
          puVar13 = (undefined4 *)OID__AllocObject();
          if (puVar13 == (undefined4 *)0x0) {
            puVar13 = (undefined4 *)0x0;
          }
          else {
            *puVar13 = 0;
          }
          CSPtrSet__AddToTail((void *)(in_stack_0000002c + 0xc0),puVar13);
          if ((*(uint *)(*(int *)(&stack0x000009dc + (int)in_stack_00000014 * 4) + 0x34) & 0x100) !=
              0) {
            iVar8 = 10;
            fStack00000034 = *(float *)(iVar14 + 4);
            in_stack_00000038 = *(float *)(iVar14 + 8);
            in_stack_0000003c = *(undefined4 *)(iVar14 + 0xc);
            in_stack_00000040 = *(undefined4 *)(iVar14 + 0x10);
            do {
              uVar15 = Random__NextLCGAbs(DAT_008a9d9c);
              uVar16 = Random__NextLCGAbs(DAT_008a9d9c);
              uVar15 = uVar15 & 0x8000ffff;
              if ((int)uVar15 < 0) {
                uVar15 = (uVar15 - 1 | 0xffff0000) + 1;
              }
              uVar16 = uVar16 & 0x8000ffff;
              if ((int)uVar16 < 0) {
                uVar16 = (uVar16 - 1 | 0xffff0000) + 1;
              }
              CDXEngine__ApplyLandscapeDamageStamp
                        (((float)(int)uVar16 * _DAT_005d8d54 - _DAT_005d85ec) * _DAT_005d85d8 +
                         fStack00000034,
                         ((float)(int)uVar15 * _DAT_005d8d54 - _DAT_005d85ec) * _DAT_005d85d8 +
                         in_stack_00000038,6);
              iVar8 = iVar8 + -1;
              in_stack_00000014 = in_stack_00000010;
            } while (iVar8 != 0);
          }
          (**(code **)(**(int **)(&stack0x000009dc + (int)in_stack_00000014 * 4) + 0xe8))();
          if (*(int **)(&stack0x000009e0 + (int)in_stack_00000014 * 4) != (int *)0x0) {
            (**(code **)(**(int **)(&stack0x000009e0 + (int)in_stack_00000014 * 4) + 4))();
          }
          *(undefined4 *)(&stack0x000009e0 + (int)in_stack_00000014 * 4) = 0;
        }
        in_stack_00000014 = in_stack_00000014 + 1;
      } while ((int)in_stack_00000014 < (int)puStack_8);
    }
    CWaypointManager__LoadWaypoints();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    DXMemBuffer__ReadBytes();
    if ((0x2c < (ushort)uStack_4) && ((ushort)uStack_4 < 0x30)) {
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
      DXMemBuffer__ReadBytes();
    }
    uVar15 = uStack_4;
    uVar5 = (ushort)uStack_4;
    if ((in_stack_000038d4 == 0) || (iStack0000001c == -1)) {
      _DAT_008a9b84 = in_stack_00000064;
      _DAT_008a9b88 = in_stack_00000074;
      _DAT_008a9b9c = in_stack_00000060;
      _DAT_008a9ba0 = in_stack_00000068;
      _DAT_008a9ba4 = in_stack_00000070;
      _DAT_008a9b90 = in_stack_00000050;
      _DAT_008a9ba8 = in_stack_0000004c;
      _DAT_008a9b94 = in_stack_00000058;
    }
    if (0x2e < uVar5) {
      if ((in_stack_000038d4 == 0) && (iStack0000001c != -1)) {
        CWorld__SkipLegacyOccupancyChunk();
        CWorld__SkipLegacyOccupancyChunk();
        CWorld__SkipLegacyOccupancyChunk();
      }
      else {
        CWorld__LoadOccupancyBitplaneChunk(DAT_00855290);
        CWorld__LoadOccupancyBitplaneChunk(DAT_00855294);
        CWorld__LoadOccupancyBitplaneChunk(DAT_00855298);
      }
      if ((uVar15 & 0xffff) < 0x32) {
        CWorld__ReadOccupancyChunkHeader();
      }
      uVar5 = (ushort)uStack_4;
    }
    if ((0x30 < uVar5) && (DXMemBuffer__ReadBytes(), in_stack_000038d4 == 0)) {
      _DAT_008a9bb0 = in_stack_00000008;
    }
    puVar13 = (undefined4 *)&stack0x00001980;
    iVar14 = 1000;
    do {
      OID__FreeObject((void *)*puVar13);
      *puVar13 = 0;
      puVar13 = puVar13 + 1;
      iVar14 = iVar14 + -1;
    } while (iVar14 != 0);
    piVar6 = *(int **)(iStack00000030 + 0x120);
    if (piVar6 == (int *)0x0) {
      iVar14 = 0;
    }
    else {
      iVar14 = *piVar6;
    }
    while (iVar14 != 0) {
      if (*(int *)(iVar14 + 4) != 0) {
        CScriptObjectCode__CollectSpawnThings();
      }
      piVar6 = (int *)piVar6[1];
      if (piVar6 == (int *)0x0) {
        iVar14 = 0;
      }
      else {
        iVar14 = *piVar6;
      }
    }
    if (in_stack_000038d4 == 0) {
      CConsole__SetLoadingFraction(&DAT_00663498,0.25);
      CWorld__SpawnInitialThings();
      CInfluenceMapManager__Update();
      CInfluenceMapManager__PropagateDistances();
      if ((ushort)uStack_4 < 0x2f) {
        CWorld__ClearOccupancyBitsUsingHeightBands();
      }
      CConsole__SetLoadingFraction(&DAT_00663498,0.5);
      if (DAT_008a9abc == 0) {
        CWorld__RebuildOccupancyGridFromDynamicSet();
      }
      else {
        CWorld__ApplyStaticMaskToOccupancyBitplanes();
      }
      CConsole__SetLoadingFraction(&DAT_00663498,1.0);
    }
    bVar22 = true;
  }
  ExceptionList = in_stack_000038c0;
  return bVar22;
}
