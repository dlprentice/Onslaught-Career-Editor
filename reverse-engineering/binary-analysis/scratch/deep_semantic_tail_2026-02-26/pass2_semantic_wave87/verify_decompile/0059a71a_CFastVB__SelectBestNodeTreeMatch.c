/* address: 0x0059a71a */
/* name: CFastVB__SelectBestNodeTreeMatch */
/* signature: int CFastVB__SelectBestNodeTreeMatch(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__SelectBestNodeTreeMatch(void)

{
  byte bVar1;
  void *pvVar2;
  undefined4 *puVar3;
  uint uVar4;
  bool bVar5;
  byte *pbVar6;
  int iVar7;
  undefined3 extraout_var;
  int iVar8;
  int extraout_EAX;
  int iVar9;
  int extraout_EAX_00;
  int extraout_EAX_01;
  int extraout_EAX_02;
  int extraout_EAX_03;
  int extraout_EAX_04;
  int extraout_EAX_05;
  int extraout_EAX_06;
  void *extraout_EAX_07;
  int extraout_EAX_08;
  int extraout_EAX_09;
  int extraout_EAX_10;
  void *in_ECX;
  int extraout_EDX;
  int *piVar10;
  byte *pbVar11;
  int *piVar12;
  char *pcVar13;
  uint unaff_EDI;
  uint uVar14;
  short *psVar15;
  char *pcVar16;
  int in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  void *in_stack_00000010;
  int in_stack_00000014;
  uint in_stack_00000018;
  int *in_stack_0000001c;
  undefined4 *in_stack_00000020;
  int local_114 [64];
  int local_14;
  uint local_10;
  void *local_c;
  uint local_8;

  if (in_stack_0000001c != (int *)0x0) {
    *in_stack_0000001c = 0;
  }
  if (in_stack_00000020 != (undefined4 *)0x0) {
    *in_stack_00000020 = 0;
  }
  local_10 = 0xffffffff;
  local_8 = 0;
  local_c = in_ECX;
  if (in_stack_00000014 != 0) {
    do {
      if (local_10 == 0) break;
      local_14 = *(int *)(in_stack_00000014 + 0x18);
      while ((local_14 != 0 && (local_10 != 0))) {
        iVar9 = *(int *)(local_14 + 8);
        pbVar11 = *(byte **)(*(int *)(iVar9 + 0x14) + 0x18);
        pbVar6 = *(byte **)(in_stack_00000008 + 8);
        do {
          bVar1 = *pbVar6;
          bVar5 = bVar1 < *pbVar11;
          if (bVar1 != *pbVar11) {
LAB_0059a79a:
            iVar8 = (1 - (uint)bVar5) - (uint)(bVar5 != 0);
            goto LAB_0059a79f;
          }
          if (bVar1 == 0) break;
          bVar1 = pbVar6[1];
          bVar5 = bVar1 < pbVar11[1];
          if (bVar1 != pbVar11[1]) goto LAB_0059a79a;
          pbVar6 = pbVar6 + 2;
          pbVar11 = pbVar11 + 2;
        } while (bVar1 != 0);
        iVar8 = 0;
LAB_0059a79f:
        if (iVar8 == 0) {
          if (in_stack_00000004 != *(int *)(iVar9 + 0x10)) {
            if ((in_stack_00000018 & 5) != 0) {
              CFastVB__Helper_00599a74((int)local_c,in_stack_00000008,0xbbd,0x5f2a60);
            }
            if (in_stack_0000001c != (int *)0x0) {
              *in_stack_0000001c = 0;
            }
            return -0x7fffbffb;
          }
          uVar14 = 0;
          if ((in_stack_00000018 & 4) != 0) {
            uVar14 = CFastVB__ScoreNodeTreeMatch
                               (local_c,*(void **)(iVar9 + 0x18),in_stack_0000000c,in_stack_00000010
                                ,in_stack_00000018,unaff_EDI);
          }
          if ((in_stack_00000018 & 8) != 0) {
            iVar8 = CFastVB__Helper_00599ffd
                              (local_c,*(int *)(iVar9 + 0x18),in_stack_0000000c,
                               (int)in_stack_00000010,in_stack_00000018);
            uVar14 = uVar14 + iVar8;
          }
          if (uVar14 != 0xffffffff) {
            if (uVar14 < local_10) {
              local_8 = 0;
              local_10 = uVar14;
            }
            uVar4 = local_8;
            if ((uVar14 == local_10) && (local_8 < 0x40)) {
              local_8 = local_8 + 1;
              local_114[uVar4] = iVar9;
            }
            if (((local_10 == 0) && (*(int *)(iVar9 + 0x2c) != 0)) && (*(int *)(iVar9 + 0x28) == 0))
            {
              iVar8 = *(int *)(in_stack_00000014 + 0x1c);
              if ((iVar8 != 0) && (*(int *)(iVar8 + 0x10) == 4)) {
                for (iVar8 = *(int *)(iVar8 + 0x18); iVar8 != 0; iVar8 = *(int *)(iVar8 + 0xc)) {
                  if (*(int *)(*(int *)(iVar8 + 8) + 0x2c) == 0) {
                    pbVar11 = *(byte **)(*(int *)(*(int *)(iVar8 + 8) + 0x14) + 0x18);
                    pbVar6 = *(byte **)(in_stack_00000008 + 8);
                    do {
                      bVar1 = *pbVar6;
                      bVar5 = bVar1 < *pbVar11;
                      if (bVar1 != *pbVar11) {
LAB_0059a880:
                        iVar7 = (1 - (uint)bVar5) - (uint)(bVar5 != 0);
                        goto LAB_0059a885;
                      }
                      if (bVar1 == 0) break;
                      bVar1 = pbVar6[1];
                      bVar5 = bVar1 < pbVar11[1];
                      if (bVar1 != pbVar11[1]) goto LAB_0059a880;
                      pbVar6 = pbVar6 + 2;
                      pbVar11 = pbVar11 + 2;
                    } while (bVar1 != 0);
                    iVar7 = 0;
LAB_0059a885:
                    if (iVar7 == 0) {
                      CFastVB__Helper_00599ac8((int)local_c,in_stack_00000008,0xc06,0x5f2ac0);
                      *(undefined4 *)(iVar9 + 0x28) = 1;
                      break;
                    }
                  }
                }
              }
              for (iVar8 = *(int *)(local_14 + 0xc); iVar8 != 0; iVar8 = *(int *)(iVar8 + 0xc)) {
                if (*(int *)(*(int *)(iVar8 + 8) + 0x2c) == 0) {
                  pbVar11 = *(byte **)(*(int *)(*(int *)(iVar8 + 8) + 0x14) + 0x18);
                  pbVar6 = *(byte **)(in_stack_00000008 + 8);
                  do {
                    bVar1 = *pbVar6;
                    bVar5 = bVar1 < *pbVar11;
                    if (bVar1 != *pbVar11) {
LAB_0059a8f4:
                      iVar7 = (1 - (uint)bVar5) - (uint)(bVar5 != 0);
                      goto LAB_0059a8f9;
                    }
                    if (bVar1 == 0) break;
                    bVar1 = pbVar6[1];
                    bVar5 = bVar1 < pbVar11[1];
                    if (bVar1 != pbVar11[1]) goto LAB_0059a8f4;
                    pbVar6 = pbVar6 + 2;
                    pbVar11 = pbVar11 + 2;
                  } while (bVar1 != 0);
                  iVar7 = 0;
LAB_0059a8f9:
                  if (iVar7 == 0) {
                    CFastVB__Helper_00599ac8((int)local_c,in_stack_00000008,0xc06,0x5f2ac0);
                    *(undefined4 *)(iVar9 + 0x28) = 1;
                    break;
                  }
                }
              }
            }
          }
        }
        local_14 = *(int *)(local_14 + 0xc);
      }
      in_stack_00000014 = *(int *)(in_stack_00000014 + 0x1c);
    } while (in_stack_00000014 != 0);
    if (local_10 != 0xffffffff) {
      if ((in_stack_00000018 & 4) != 0) {
        iVar9 = *(int *)(local_114[0] + 0x18);
        uVar14 = 1;
        if (1 < local_8) {
          do {
            bVar5 = CFastVB__Helper_00599cd2
                              (*(int *)(iVar9 + 0x20),
                               *(int *)(*(int *)(local_114[uVar14] + 0x18) + 0x20));
            if ((CONCAT31(extraout_var,bVar5) == 0) ||
               (iVar8 = CFastVB__Helper_00599ffd
                                  (local_c,iVar9,*(int *)(iVar9 + 0x1c),
                                   *(int *)(extraout_EDX + 0x24),0), iVar8 == -1)) break;
            uVar14 = uVar14 + 1;
          } while (uVar14 < local_8);
          if (uVar14 < local_8) {
            CFastVB__Helper_00599a74((int)local_c,in_stack_00000008,0xbfb,0x5f2aa0);
          }
        }
      }
      piVar10 = in_stack_0000001c;
      if (in_stack_0000001c != (int *)0x0) {
        pvVar2 = *(void **)(local_114[0] + 0x18);
        if ((in_stack_00000018 & 2) == 0) {
          if (pvVar2 != (void *)0x0) {
            iVar9 = CFastVB__Helper_0059879e(pvVar2);
            *in_stack_0000001c = iVar9;
            if (iVar9 == 0) {
              return -0x7ff8fff2;
            }
          }
        }
        else {
          *in_stack_0000001c = (int)pvVar2;
        }
      }
      if (in_stack_00000020 == (undefined4 *)0x0) {
        return 0;
      }
      uVar14 = 0;
      in_stack_0000001c = (undefined4 *)0x0;
      piVar12 = (int *)&stack0x0000001c;
      if (local_8 != 0) {
        do {
          CFastVB__Helper_00426fd0(0x14);
          if (extraout_EAX == 0) {
            iVar9 = 0;
          }
          else {
            iVar9 = CTexture__Helper_005987f4();
          }
          *piVar12 = iVar9;
          if (iVar9 == 0) {
LAB_0059aabd:
            if (in_stack_0000001c != (undefined4 *)0x0) {
              (**(code **)*in_stack_0000001c)(1);
            }
            if (piVar10 == (int *)0x0) {
              return -0x7ff8fff2;
            }
            if ((in_stack_00000018 & 2) != 0) {
              return -0x7ff8fff2;
            }
            puVar3 = (undefined4 *)*piVar10;
            if (puVar3 == (undefined4 *)0x0) {
              return -0x7ff8fff2;
            }
            (**(code **)*puVar3)(1);
            return -0x7ff8fff2;
          }
          CFastVB__Helper_00426fd0(0x40);
          if (extraout_EAX_00 == 0) {
            iVar9 = 0;
          }
          else {
            iVar9 = CFastVB__Helper_00598da4();
          }
          *(int *)(*piVar12 + 8) = iVar9;
          if (iVar9 == 0) goto LAB_0059aabd;
          piVar12 = (int *)(*piVar12 + 0xc);
          uVar14 = uVar14 + 1;
        } while (uVar14 < local_8);
      }
      *in_stack_00000020 = in_stack_0000001c;
      return 0;
    }
  }
  if (((in_stack_00000018 & 2) != 0) || (in_stack_00000020 != (undefined4 *)0x0)) goto LAB_0059ae8d;
  if (in_stack_00000004 != 0) {
    if (in_stack_00000004 == 1) {
      iVar9 = 5;
      bVar5 = true;
      pcVar13 = *(char **)(in_stack_00000008 + 8);
      pcVar16 = "NULL";
      do {
        if (iVar9 == 0) break;
        iVar9 = iVar9 + -1;
        bVar5 = *pcVar13 == *pcVar16;
        pcVar13 = pcVar13 + 1;
        pcVar16 = pcVar16 + 1;
      } while (bVar5);
      if (bVar5) {
        if (in_stack_0000001c == (int *)0x0) {
          return 0;
        }
        CFastVB__Helper_00426fd0(0x3c);
        if (extraout_EAX_07 == (void *)0x0) {
          iVar9 = 0;
        }
        else {
          CFastVB__InitNodeType10(extraout_EAX_07);
          iVar9 = extraout_EAX_08;
        }
        if (iVar9 == 0) {
          return -0x7ff8fff2;
        }
        *(undefined4 *)(iVar9 + 0x18) = 0;
        *(undefined4 *)(iVar9 + 0x14) = 1;
        *(undefined4 *)(iVar9 + 0x1c) = 0x202;
        CFastVB__Helper_00426fd0(0x24);
        if (extraout_EAX_09 == 0) {
          iVar8 = 0;
        }
        else {
          iVar8 = CFastVB__Helper_00598a81();
        }
        *(int *)(iVar9 + 0x20) = iVar8;
        if (iVar8 == 0) {
          return -0x7ff8fff2;
        }
        CFastVB__Helper_00426fd0(0x40);
        if (extraout_EAX_10 == 0) {
          iVar8 = 0;
        }
        else {
          iVar8 = CFastVB__Helper_00598ddc();
        }
        *(int *)(iVar9 + 0x24) = iVar8;
        if (iVar8 == 0) {
          return -0x7ff8fff2;
        }
        *in_stack_0000001c = iVar9;
        return 0;
      }
    }
    goto LAB_0059ae8d;
  }
  iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"dword");
  if ((iVar9 == 0) || (iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"float"), iVar9 == 0)) {
    if (in_stack_0000001c == (int *)0x0) {
      return 0;
    }
    CFastVB__Helper_00426fd0(0x24);
    iVar9 = extraout_EAX_01;
joined_r0x0059ac5f:
    if (iVar9 == 0) {
      iVar9 = 0;
    }
    else {
      iVar9 = CFastVB__Helper_00598a81();
    }
    *in_stack_0000001c = iVar9;
    goto LAB_0059ab66;
  }
  iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"vector");
  if (iVar9 == 0) {
    if (in_stack_0000001c == (int *)0x0) {
      return 0;
    }
    CFastVB__Helper_00426fd0(0x24);
    if (extraout_EAX_02 != 0) goto LAB_0059aba7;
LAB_0059abe6:
    iVar9 = 0;
  }
  else {
    iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"matrix");
    if (iVar9 != 0) {
      iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"string");
      if ((((iVar9 == 0) ||
           (iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"texture"), iVar9 == 0)) ||
          (iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"pixelshader"), iVar9 == 0)) ||
         (iVar9 = stricmp(*(char **)(in_stack_00000008 + 8),"vertexshader"), iVar9 == 0)) {
        if (in_stack_0000001c == (int *)0x0) {
          return 0;
        }
        CFastVB__Helper_00426fd0(0x24);
        iVar9 = extraout_EAX_04;
        goto joined_r0x0059ac5f;
      }
      piVar10 = *(int **)(in_stack_00000008 + 8);
      piVar12 = piVar10;
      do {
        iVar9 = *piVar12;
        piVar12 = (int *)((int)piVar12 + 1);
      } while ((char)iVar9 != '\0');
      uVar14 = (int)piVar12 - (int)((int)piVar10 + 1);
      iVar9 = 3;
      if ((uVar14 < 4) || (*piVar10 != DAT_005f2900)) {
        if (2 < uVar14) {
          bVar5 = true;
          piVar12 = piVar10;
          pcVar13 = "int";
          do {
            if (iVar9 == 0) break;
            iVar9 = iVar9 + -1;
            bVar5 = (char)*piVar12 == *pcVar13;
            piVar12 = (int *)((int)piVar12 + 1);
            pcVar13 = pcVar13 + 1;
          } while (bVar5);
          if (bVar5) {
            piVar10 = (int *)((int)piVar10 + 3);
            iVar9 = uVar14 - 3;
            goto LAB_0059ad23;
          }
        }
        if ((uVar14 < 4) || (*piVar10 != DAT_005f28f4)) {
          if (4 < uVar14) {
            iVar9 = 5;
            bVar5 = true;
            piVar12 = piVar10;
            pcVar13 = "float";
            do {
              if (iVar9 == 0) break;
              iVar9 = iVar9 + -1;
              bVar5 = (char)*piVar12 == *pcVar13;
              piVar12 = (int *)((int)piVar12 + 1);
              pcVar13 = pcVar13 + 1;
            } while (bVar5);
            if (bVar5) {
              piVar10 = (int *)((int)piVar10 + 5);
              iVar9 = uVar14 - 5;
              goto LAB_0059ad23;
            }
          }
          if (uVar14 < 6) goto LAB_0059ae8d;
          iVar9 = 3;
          bVar5 = true;
          piVar12 = piVar10;
          psVar15 = (short *)"double";
          do {
            if (iVar9 == 0) break;
            iVar9 = iVar9 + -1;
            bVar5 = (short)*piVar12 == *psVar15;
            piVar12 = (int *)((int)piVar12 + 2);
            psVar15 = psVar15 + 1;
          } while (bVar5);
          if (!bVar5) goto LAB_0059ae8d;
          piVar10 = (int *)((int)piVar10 + 6);
          iVar9 = uVar14 - 6;
        }
        else {
          piVar10 = piVar10 + 1;
          iVar9 = uVar14 - 4;
        }
      }
      else {
        piVar10 = piVar10 + 1;
        iVar9 = uVar14 - 4;
      }
LAB_0059ad23:
      if (iVar9 == 1) {
        if (((char)*piVar10 < '1') || ('4' < (char)*piVar10)) {
LAB_0059ae8d:
          if ((in_stack_00000018 & 1) != 0) {
            CFastVB__Helper_00599a74((int)local_c,in_stack_00000008,0xbbc,0x5f2a2c);
          }
          return 1;
        }
        if (in_stack_0000001c == (int *)0x0) {
          return 0;
        }
        CFastVB__Helper_00426fd0(0x24);
        if (extraout_EAX_05 != 0) goto LAB_0059ad5e;
LAB_0059adcb:
        iVar9 = 0;
      }
      else {
        if ((((iVar9 != 3) || ((char)*piVar10 < '1')) || ('4' < (char)*piVar10)) ||
           (((*(char *)((int)piVar10 + 1) != 'x' || (*(char *)((int)piVar10 + 2) < '1')) ||
            ('4' < *(char *)((int)piVar10 + 2))))) goto LAB_0059ae8d;
        if (in_stack_0000001c == (int *)0x0) {
          return 0;
        }
        CFastVB__Helper_00426fd0(0x24);
        if (extraout_EAX_06 == 0) goto LAB_0059adcb;
LAB_0059ad5e:
        iVar9 = CFastVB__Helper_00598a81();
      }
      *in_stack_0000001c = iVar9;
      goto LAB_0059ab66;
    }
    if (in_stack_0000001c == (int *)0x0) {
      return 0;
    }
    CFastVB__Helper_00426fd0(0x24);
    if (extraout_EAX_03 == 0) goto LAB_0059abe6;
LAB_0059aba7:
    iVar9 = CFastVB__Helper_00598a81();
  }
  *in_stack_0000001c = iVar9;
LAB_0059ab66:
  if (iVar9 != 0) {
    return 0;
  }
  return -0x7ff8fff2;
}
