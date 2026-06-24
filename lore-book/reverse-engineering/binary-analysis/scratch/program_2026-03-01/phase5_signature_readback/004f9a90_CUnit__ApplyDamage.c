/* address: 0x004f9a90 */
/* name: CUnit__ApplyDamage */
/* signature: void __thiscall CUnit__ApplyDamage(void * this, float damageAmount, int damageType) */


/* WARNING: Removing unreachable block (ram,0x004f9d15) */
/* WARNING: Removing unreachable block (ram,0x004f9d30) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnit__ApplyDamage(void *this,float damageAmount,int damageType)

{
  int *piVar1;
  byte bVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  void *this_00;
  int iVar6;
  byte *pbVar7;
  int iVar8;
  byte *pbVar9;
  short *psVar10;
  char *pcVar11;
  void *unaff_EDI;
  int iVar12;
  bool bVar13;
  int in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_ffffff00;
  float fStack_90;
  float fStack_8c;
  float fStack_88;
  undefined **ppuStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  float fStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d55b4;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  if ((((*(int *)((int)this + 0x148) != 0) &&
       (ExceptionList = &local_c, (*(byte *)(damageType + 0x34) & 4) != 0)) &&
      (ExceptionList = &local_c, *(int *)(damageType + 0xec) != 0)) &&
     (ExceptionList = &local_c, (*(byte *)(*(int *)(damageType + 0xec) + 0x34) & 0x10) != 0)) {
    ExceptionList = &local_c;
    CUnit__ResetDamageCooldownTimer(*(int *)((int)this + 0x148));
  }
  if ((((*(byte *)((int)this + 0x2c) & 4) != 0) && ((*(uint *)(damageType + 0x34) & 0x1000000) != 0)
      ) && (*(int *)(*(int *)((int)this + 0x164) + 0x124) != 0)) {
    ExceptionList = local_c;
    return;
  }
  iVar12 = *(int *)((int)this + 0x244);
  if (((iVar12 == 4) || (iVar12 == 3)) || (iVar12 == 5)) {
    damageAmount = damageAmount * *(float *)(*(int *)((int)this + 0x164) + 0x160);
  }
  if (damageAmount <= _DAT_005d856c) {
    iVar12 = *(int *)((int)this + 0x164);
    if ((*(float *)((int)this + 0xf8) < *(float *)(iVar12 + 0xc0)) &&
       (_DAT_005d856c < *(float *)((int)this + 0xf8))) {
      if (-damageAmount <= *(float *)(iVar12 + 0xc0) - *(float *)((int)this + 0xf8)) {
        *(float *)((int)this + 0xf8) = *(float *)((int)this + 0xf8) - damageAmount;
      }
      else {
        *(undefined4 *)((int)this + 0xf8) = *(undefined4 *)(iVar12 + 0xc0);
      }
    }
  }
  else {
    if (*(int *)((int)this + 0x15c) == 0) {
      ExceptionList = local_c;
      return;
    }
    if ((*(int *)((int)this + 0x228) != 0) && ((*(uint *)(damageType + 0x34) & 0x1000000) != 0)) {
      ExceptionList = local_c;
      return;
    }
    if ((*(int *)((int)this + 0x228) != 0) && (in_stack_00000010 != -1)) {
      if ((*(uint *)(damageType + 0x34) & 0x1000000) != 0) {
        for (iVar12 = 0; iVar6 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))(),
            iVar12 < *(int *)(iVar6 + 0x15c); iVar12 = iVar12 + 1) {
          iVar6 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
          iVar6 = *(int *)(*(int *)(iVar6 + 0x160) + iVar12 * 4);
          if ((iVar6 != 0) && (iVar6 = stricmp((char *)(iVar6 + 0xdc),s_nexus_00633af4), iVar6 == 0)
             ) break;
        }
        CMCMech__BuildInterpolatedPoseAndAnchor();
        uStack_6c = 0;
        uStack_68 = 0;
        fStack_4c = *(float *)(damageType + 0x1c);
        uStack_64 = 0;
        ppuStack_70 = &PTR_VFuncSlot_00_00426340_005d8bfc;
        uStack_48 = *(undefined4 *)(damageType + 0x20);
        uStack_44 = *(undefined4 *)(damageType + 0x24);
        uStack_40 = *(undefined4 *)(damageType + 0x28);
        fVar3 = fStack_88 - *(float *)(damageType + 0x24);
        fVar5 = fStack_8c - *(float *)(damageType + 0x20);
        fVar4 = fStack_90 - *(float *)(damageType + 0x1c);
        uStack_4 = 0;
        if (*(float *)(damageType + 0x7c) < SQRT(fVar3 * fVar3 + fVar5 * fVar5 + fVar4 * fVar4)) {
          ExceptionList = local_c;
          return;
        }
        CGeneralVolume__ctor_like_004098e0(&stack0xffffff00,&ppuStack_70,in_stack_ffffff00);
        OID__TraceLineAndSelectBestTargetHit();
        ExceptionList = local_c;
        return;
      }
      iVar12 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
      iVar12 = *(int *)(*(int *)(iVar12 + 0x160) + in_stack_00000010 * 4);
      if ((iVar12 != 0) && (iVar12 = stricmp((char *)(iVar12 + 0xdc),s_nexus_00633af4), iVar12 != 0)
         ) {
        ExceptionList = local_c;
        return;
      }
    }
    if ((*(int *)((int)this + 0x22c) != 0) && (in_stack_00000010 != -1)) {
      iVar12 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
      iVar12 = *(int *)(*(int *)(iVar12 + 0x160) + in_stack_00000010 * 4);
      if ((iVar12 != 0) &&
         (iVar12 = stricmp((char *)(iVar12 + 0xdc),s_weakpoint_00633ae8), iVar12 != 0)) {
        damageAmount = damageAmount * _DAT_005d85d8;
      }
    }
    if (*(void **)((int)this + 0x178) != (void *)0x0) {
      CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold
                (*(void **)((int)this + 0x178),in_stack_00000010,(int)damageAmount,damageType,
                 (int)unaff_EDI);
      ExceptionList = local_c;
      return;
    }
    (**(code **)(*(int *)this + 0x1ac))();
    if (in_stack_0000000c != 0) {
      if (damageAmount <= *(float *)((int)this + 0x100)) {
        *(float *)((int)this + 0x100) = *(float *)((int)this + 0x100) - damageAmount;
        ExceptionList = local_c;
        return;
      }
      if (*(float *)((int)this + 0x100) < damageAmount) {
        damageAmount = damageAmount - *(float *)((int)this + 0x100);
        *(undefined4 *)((int)this + 0x100) = 0;
      }
    }
    fVar3 = *(float *)((int)this + 0xf8) - damageAmount;
    *(float *)((int)this + 0xf8) = fVar3;
    if ((fVar3 < _DAT_005d856c) && ((*(byte *)((int)this + 0x2c) & 4) == 0)) {
      if (((*(byte *)(damageType + 0x34) & 4) != 0) &&
         ((iVar12 = *(int *)(damageType + 0xec), iVar12 != 0 &&
          ((*(byte *)(iVar12 + 0x34) & 8) != 0)))) {
        piVar1 = (int *)(*(int *)(iVar12 + 0x574) + 0x30);
        *piVar1 = *piVar1 + 1;
      }
      if (*(int *)(*(int *)((int)this + 0x164) + 0x11c) == 0) {
        (**(code **)(*(int *)this + 200))();
        (**(code **)(*(int *)this + 0x11c))();
      }
      *(undefined4 *)((int)this + 0x1f0) = 0;
    }
    if ((_DAT_005d8ba0 < *(float *)((int)this + 0x100)) && (**(int **)((int)this + 0x164) != 0)) {
      CParticleManager__CreateEffect();
    }
  }
  if ((*(int *)(*(int *)((int)this + 0x164) + 0x11c) != 0) &&
     (*(float *)((int)this + 0xf8) < _DAT_005d856c)) {
    (**(code **)(*(int *)this + 400))();
  }
  if (*(int *)(*(int *)((int)this + 0x164) + 0x120) != 0) {
    psVar10 = (short *)0x0;
    iVar12 = Random__NextLCGAbs(DAT_008a9d9c);
    pcVar11 = s_Tara_Fighter_00633b98;
    iVar12 = iVar12 % 3;
    iVar6 = 0;
    pbVar9 = *(byte **)(*(int *)((int)this + 0x164) + 0xb0);
    pbVar7 = pbVar9;
    do {
      bVar2 = *pbVar7;
      bVar13 = bVar2 < (byte)*pcVar11;
      if (bVar2 != *pcVar11) {
LAB_004fa037:
        iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
        goto LAB_004fa03c;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar7[1];
      bVar13 = bVar2 < (byte)pcVar11[1];
      if (bVar2 != pcVar11[1]) goto LAB_004fa037;
      pbVar7 = pbVar7 + 2;
      pcVar11 = pcVar11 + 2;
    } while (bVar2 != 0);
    iVar8 = 0;
LAB_004fa03c:
    if (iVar8 == 0) {
      iVar8 = 0x3c345;
    }
    else {
      pcVar11 = s_Billy_Fighter_00633b88;
      do {
        bVar2 = *pbVar9;
        bVar13 = bVar2 < (byte)*pcVar11;
        if (bVar2 != *pcVar11) {
LAB_004fa072:
          iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
          goto LAB_004fa077;
        }
        if (bVar2 == 0) break;
        bVar2 = pbVar9[1];
        bVar13 = bVar2 < (byte)pcVar11[1];
        if (bVar2 != pcVar11[1]) goto LAB_004fa072;
        pbVar9 = pbVar9 + 2;
        pcVar11 = pcVar11 + 2;
      } while (bVar2 != 0);
      iVar8 = 0;
LAB_004fa077:
      if (iVar8 == 0) {
        iVar8 = 0xcb1fd;
      }
      else {
        iVar8 = 0x19f8cf;
      }
    }
    CText__GetStringById(&g_Text,iVar8);
    if ((_DAT_005d856c <= *(float *)((int)this + 0xf8)) || (*(int *)((int)this + 0x23c) != 0)) {
      iVar8 = *(int *)((int)this + 0x164);
      if ((*(float *)(iVar8 + 0xc0) * _DAT_005d858c <= *(float *)((int)this + 0xf8)) ||
         (*(int *)((int)this + 0x238) != 0)) {
        if ((*(float *)((int)this + 0xf8) < *(float *)(iVar8 + 0xc0) * _DAT_005d85ec) &&
           (*(int *)((int)this + 0x234) == 0)) {
          pbVar9 = *(byte **)(iVar8 + 0xb0);
          pcVar11 = s_Tara_Fighter_00633b98;
          pbVar7 = pbVar9;
          do {
            bVar2 = *pbVar7;
            bVar13 = bVar2 < (byte)*pcVar11;
            if (bVar2 != *pcVar11) {
LAB_004fa35d:
              iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
              goto LAB_004fa362;
            }
            if (bVar2 == 0) break;
            bVar2 = pbVar7[1];
            bVar13 = bVar2 < (byte)pcVar11[1];
            if (bVar2 != pcVar11[1]) goto LAB_004fa35d;
            pbVar7 = pbVar7 + 2;
            pcVar11 = pcVar11 + 2;
          } while (bVar2 != 0);
          iVar8 = 0;
LAB_004fa362:
          if (iVar8 == 0) {
            if (iVar12 == 0) {
              iVar6 = 0xa896430;
            }
            else if (iVar12 == 1) {
              iVar6 = 0xe7cd233;
            }
            else if (iVar12 == 2) {
              iVar6 = 0x12704036;
            }
          }
          else {
            pcVar11 = s_Billy_Fighter_00633b88;
            do {
              bVar2 = *pbVar9;
              bVar13 = bVar2 < (byte)*pcVar11;
              if (bVar2 != *pcVar11) {
LAB_004fa3bc:
                iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
                goto LAB_004fa3c1;
              }
              if (bVar2 == 0) break;
              bVar2 = pbVar9[1];
              bVar13 = bVar2 < (byte)pcVar11[1];
              if (bVar2 != pcVar11[1]) goto LAB_004fa3bc;
              pbVar9 = pbVar9 + 2;
              pcVar11 = pcVar11 + 2;
            } while (bVar2 != 0);
            iVar8 = 0;
LAB_004fa3c1:
            if (iVar8 == 0) {
              if (iVar12 == 0) {
                iVar6 = 0x3f443bff;
              }
              else if (iVar12 == 1) {
                iVar6 = 0x472b1662;
              }
              else if (iVar12 == 2) {
                iVar6 = 0x4f11f0c5;
              }
            }
            else if (iVar12 == 0) {
              iVar6 = 0x2ef87634;
            }
            else if (iVar12 == 1) {
              iVar6 = 0x36df5145;
            }
            else if (iVar12 == 2) {
              iVar6 = 0x3ec62c56;
            }
          }
          psVar10 = CText__GetStringById(&g_Text,iVar6);
          *(undefined4 *)((int)this + 0x234) = 1;
        }
      }
      else {
        pbVar9 = *(byte **)(iVar8 + 0xb0);
        pcVar11 = s_Tara_Fighter_00633b98;
        pbVar7 = pbVar9;
        do {
          bVar2 = *pbVar7;
          bVar13 = bVar2 < (byte)*pcVar11;
          if (bVar2 != *pcVar11) {
LAB_004fa230:
            iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
            goto LAB_004fa235;
          }
          if (bVar2 == 0) break;
          bVar2 = pbVar7[1];
          bVar13 = bVar2 < (byte)pcVar11[1];
          if (bVar2 != pcVar11[1]) goto LAB_004fa230;
          pbVar7 = pbVar7 + 2;
          pcVar11 = pcVar11 + 2;
        } while (bVar2 != 0);
        iVar8 = 0;
LAB_004fa235:
        if (iVar8 == 0) {
          if (iVar12 == 0) {
            iVar6 = 0x1604fe0a;
          }
          else if (iVar12 == 1) {
            iVar6 = 0x1decf40d;
          }
          else if (iVar12 == 2) {
            iVar6 = 0x25d4ea10;
          }
        }
        else {
          pcVar11 = s_Billy_Fighter_00633b88;
          do {
            bVar2 = *pbVar9;
            bVar13 = bVar2 < (byte)*pcVar11;
            if (bVar2 != *pcVar11) {
LAB_004fa28f:
              iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
              goto LAB_004fa294;
            }
            if (bVar2 == 0) break;
            bVar2 = pbVar9[1];
            bVar13 = bVar2 < (byte)pcVar11[1];
            if (bVar2 != pcVar11[1]) goto LAB_004fa28f;
            pbVar9 = pbVar9 + 2;
            pcVar11 = pcVar11 + 2;
          } while (bVar2 != 0);
          iVar8 = 0;
LAB_004fa294:
          if (iVar8 == 0) {
            if (iVar12 == 0) {
              iVar6 = -0x7fe77aa7;
            }
            else if (iVar12 == 1) {
              iVar6 = -0x70179044;
            }
            else if (iVar12 == 2) {
              iVar6 = -0x6047a5e1;
            }
          }
          else if (iVar12 == 0) {
            iVar6 = 0x5f7c0e8e;
          }
          else if (iVar12 == 1) {
            iVar6 = 0x6f4bf99f;
          }
          else if (iVar12 == 2) {
            iVar6 = 0x7f1be4b0;
          }
        }
        psVar10 = CText__GetStringById(&g_Text,iVar6);
        *(undefined4 *)((int)this + 0x238) = 1;
        *(undefined4 *)((int)this + 0x234) = 1;
      }
    }
    else {
      pcVar11 = s_Tara_Fighter_00633b98;
      pbVar9 = *(byte **)(*(int *)((int)this + 0x164) + 0xb0);
      pbVar7 = pbVar9;
      do {
        bVar2 = *pbVar7;
        bVar13 = bVar2 < (byte)*pcVar11;
        if (bVar2 != *pcVar11) {
LAB_004fa0f7:
          iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
          goto LAB_004fa0fc;
        }
        if (bVar2 == 0) break;
        bVar2 = pbVar7[1];
        bVar13 = bVar2 < (byte)pcVar11[1];
        if (bVar2 != pcVar11[1]) goto LAB_004fa0f7;
        pbVar7 = pbVar7 + 2;
        pcVar11 = pcVar11 + 2;
      } while (bVar2 != 0);
      iVar8 = 0;
LAB_004fa0fc:
      if (iVar8 == 0) {
        if (iVar12 == 0) {
          iVar6 = 0xb2cb1a4;
        }
        else if (iVar12 == 1) {
          iVar6 = 0xf20c0e7;
        }
        else if (iVar12 == 2) {
          iVar6 = 0x1314d02a;
        }
      }
      else {
        pcVar11 = s_Billy_Fighter_00633b88;
        do {
          bVar2 = *pbVar9;
          bVar13 = bVar2 < (byte)*pcVar11;
          if (bVar2 != *pcVar11) {
LAB_004fa156:
            iVar8 = (1 - (uint)bVar13) - (uint)(bVar13 != 0);
            goto LAB_004fa15b;
          }
          if (bVar2 == 0) break;
          bVar2 = pbVar9[1];
          bVar13 = bVar2 < (byte)pcVar11[1];
          if (bVar2 != pcVar11[1]) goto LAB_004fa156;
          pbVar9 = pbVar9 + 2;
          pcVar11 = pcVar11 + 2;
        } while (bVar2 != 0);
        iVar8 = 0;
LAB_004fa15b:
        if (iVar8 == 0) {
          if (iVar12 == 0) {
            iVar6 = 0x4041921f;
          }
          else if (iVar12 == 1) {
            iVar6 = 0x4829af02;
          }
          else if (iVar12 == 2) {
            iVar6 = 0x5011cbe5;
          }
        }
        else if (iVar12 == 0) {
          iVar6 = 0x2ff3332c;
        }
        else if (iVar12 == 1) {
          iVar6 = 0x37db50bd;
        }
        else if (iVar12 == 2) {
          iVar6 = 0x3fc36e4e;
        }
      }
      psVar10 = CText__GetStringById(&g_Text,iVar6);
      *(undefined4 *)((int)this + 0x23c) = 1;
      *(undefined4 *)((int)this + 0x238) = 1;
      *(undefined4 *)((int)this + 0x234) = 1;
    }
    this_00 = DAT_008a9d84;
    if ((DAT_008a9d84 != (void *)0x0) && (psVar10 != (short *)0x0)) {
      iVar12 = OID__AllocObject();
      uStack_4 = 1;
      if (iVar12 == 0) {
        iVar12 = 0;
      }
      else {
        iVar12 = CMessage__ctor_like_004b6e50();
      }
      uStack_4 = 0xffffffff;
      IScript__InsertSortedAndTryAdvancePortrait(this_00,iVar12,unaff_EDI);
    }
  }
  ExceptionList = local_c;
  return;
}
