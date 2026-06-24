/* address: 0x00565083 */
/* name: ControlsUI__Helper_00565083 */
/* signature: int __cdecl ControlsUI__Helper_00565083(int param_1, void * param_2, void * param_3) */


int __cdecl ControlsUI__Helper_00565083(int param_1,void *param_2,void *param_3)

{
  short sVar1;
  void *pvVar2;
  uint uVar3;
  byte *pbVar4;
  short *psVar5;
  int *piVar6;
  byte *pbVar7;
  int extraout_EDX;
  ushort uVar8;
  undefined4 unaff_EBX;
  byte *pbVar9;
  int iVar10;
  bool bVar11;
  longlong lVar12;
  undefined2 local_454;
  byte local_255 [513];
  undefined4 local_54;
  undefined4 local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  undefined4 local_38;
  int local_34;
  int local_30;
  int local_2c;
  undefined1 local_26;
  undefined1 local_25;
  undefined2 local_24;
  short local_22;
  int local_20;
  int local_1c;
  int local_18;
  int local_14;
  byte *local_10;
  byte *local_c;
  byte *local_8;

  local_3c = 0;
  sVar1 = *(short *)param_2;
  pbVar9 = (byte *)CONCAT22((short)((uint)unaff_EBX >> 0x10),sVar1);
  local_c = (byte *)0x0;
  local_18 = 0;
  pvVar2 = param_2;
  do {
    if ((sVar1 == 0) || (param_2 = (void *)((int)pvVar2 + 2), local_18 < 0)) {
      return local_18;
    }
    uVar8 = (ushort)pbVar9;
    if ((uVar8 < 0x20) || (0x78 < uVar8)) {
      uVar3 = 0;
    }
    else {
      uVar3 = (byte)(&DAT_005e5c14)[(uint)pbVar9 & 0xffff] & 0xf;
    }
    local_3c = (int)(char)(&DAT_005e5c34)[uVar3 * 8 + local_3c] >> 4;
    switch(local_3c) {
    case 0:
switchD_005650f1_caseD_0:
      local_20 = 1;
      ControlsUI__Helper_005657d0((int)pbVar9,param_1,&local_18);
      break;
    case 1:
      local_14 = -1;
      local_38 = 0;
      local_34 = 0;
      local_2c = 0;
      local_1c = 0;
      local_8 = (byte *)0x0;
      local_20 = 0;
      break;
    case 2:
      uVar3 = (uint)pbVar9 & 0xffff;
      if (uVar3 == 0x20) {
        local_8 = (byte *)((uint)local_8 | 2);
      }
      else if (uVar3 == 0x23) {
        local_8 = (byte *)((uint)local_8 | 0x80);
      }
      else if (uVar3 == 0x2b) {
        local_8 = (byte *)((uint)local_8 | 1);
      }
      else if (uVar3 == 0x2d) {
        local_8 = (byte *)((uint)local_8 | 4);
      }
      else if (uVar3 == 0x30) {
        local_8 = (byte *)((uint)local_8 | 8);
      }
      break;
    case 3:
      if (uVar8 == 0x2a) {
        local_2c = ControlsUI__Helper_00562013(&param_3);
        if (local_2c < 0) {
          local_8 = (byte *)((uint)local_8 | 4);
          local_2c = -local_2c;
        }
      }
      else {
        local_2c = (((uint)pbVar9 & 0xffff) - 0x30) + local_2c * 10;
      }
      break;
    case 4:
      local_14 = 0;
      break;
    case 5:
      if (uVar8 == 0x2a) {
        local_14 = ControlsUI__Helper_00562013(&param_3);
        if (local_14 < 0) {
          local_14 = -1;
        }
      }
      else {
        local_14 = (((uint)pbVar9 & 0xffff) - 0x30) + local_14 * 10;
      }
      break;
    case 6:
      uVar3 = (uint)pbVar9 & 0xffff;
      if (uVar3 == 0x49) {
        if ((*(short *)param_2 != 0x36) || (*(short *)((int)pvVar2 + 4) != 0x34)) {
          local_3c = 0;
          goto switchD_005650f1_caseD_0;
        }
        param_2 = (void *)((int)pvVar2 + 6);
        local_8 = (byte *)((uint)local_8 | 0x8000);
      }
      else if (uVar3 == 0x68) {
        local_8 = (byte *)((uint)local_8 | 0x20);
      }
      else if (uVar3 == 0x77) {
        local_8 = (byte *)((uint)local_8 | 0x800);
      }
      break;
    case 7:
      uVar3 = (uint)pbVar9 & 0xffff;
      pbVar4 = local_10;
      if (uVar3 < 0x68) {
        if (uVar3 < 0x65) {
          if (uVar3 < 0x59) {
            if (uVar3 == 0x58) {
LAB_005654f7:
              local_30 = 7;
LAB_005654fa:
              local_c = (byte *)0x10;
              if (((uint)local_8 & 0x80) != 0) {
                local_24 = 0x30;
                local_22 = (short)local_30 + 0x51;
                local_1c = 2;
              }
              goto LAB_00565568;
            }
            if (uVar3 != 0x43) {
              if ((uVar3 != 0x45) && (uVar3 != 0x47)) {
                if (uVar3 == 0x53) {
                  if (((uint)local_8 & 0x830) == 0) {
                    local_8 = (byte *)((uint)local_8 | 0x20);
                  }
                  goto LAB_00565288;
                }
                goto LAB_00565689;
              }
              local_38 = 1;
              pbVar9 = pbVar9 + 0x20;
              goto LAB_005652f9;
            }
            if (((uint)local_8 & 0x830) == 0) {
              local_8 = (byte *)((uint)local_8 | 0x20);
            }
LAB_00565326:
            local_20 = 1;
            local_40 = ControlsUI__Helper_00562013(&param_3);
            if (((uint)local_8 & 0x20) == 0) {
              local_454 = (undefined2)local_40;
            }
            else {
              local_25 = 0;
              local_26 = (undefined1)local_40;
              iVar10 = CRT__MultiByteToWideChar_ThreadSafe
                                 ((int)&local_454,(int)&local_26,DAT_00653a9c);
              if (iVar10 < 0) {
                local_34 = 1;
              }
            }
            local_c = (byte *)0x1;
            pbVar4 = (byte *)&local_454;
          }
          else if (uVar3 == 0x5a) {
            psVar5 = (short *)ControlsUI__Helper_00562013(&param_3);
            if ((psVar5 == (short *)0x0) || (pbVar4 = *(byte **)(psVar5 + 2), pbVar4 == (byte *)0x0)
               ) {
              local_10 = PTR_DAT_00653760;
              pbVar4 = PTR_DAT_00653760;
              goto LAB_005653e2;
            }
            if (((uint)local_8 & 0x800) == 0) {
              local_c = (byte *)(int)*psVar5;
              local_20 = 0;
            }
            else {
              local_c = (byte *)((uint)(int)*psVar5 >> 1);
              local_20 = 1;
            }
          }
          else {
            if (uVar3 == 99) goto LAB_00565326;
            if (uVar3 == 100) goto LAB_0056555d;
          }
        }
        else {
LAB_005652f9:
          local_8 = (byte *)((uint)local_8 | 0x40);
          pbVar4 = (byte *)&local_454;
          if (local_14 < 0) {
            local_14 = 6;
          }
          else if ((local_14 == 0) && ((short)pbVar9 == 0x67)) {
            local_14 = 1;
          }
          local_54 = *(undefined4 *)param_3;
          local_50 = *(undefined4 *)((int)param_3 + 4);
          param_3 = (undefined4 *)((int)param_3 + 8);
          local_10 = pbVar4;
          (*(code *)PTR_ControlsUI__Helper_00569cb8_00653658)
                    (&local_54,&local_454,(int)(char)pbVar9,local_14,local_38);
          uVar3 = (uint)local_8 & 0x80;
          if ((uVar3 != 0) && (local_14 == 0)) {
            (*(code *)PTR_ControlsUI__Helper_00569cb8_00653664)(&local_454);
          }
          if (((short)pbVar9 == 0x67) && (uVar3 == 0)) {
            (*(code *)PTR_ControlsUI__Helper_00569cb8_0065365c)(&local_454);
          }
          if ((byte)local_454 == 0x2d) {
            local_8 = (byte *)((uint)local_8 | 0x100);
            pbVar4 = (byte *)((int)&local_454 + 1);
            local_10 = pbVar4;
          }
LAB_005653e2:
          local_c = (byte *)_strlen((char *)pbVar4);
          pbVar4 = local_10;
        }
      }
      else {
        if (uVar3 == 0x69) {
LAB_0056555d:
          local_8 = (byte *)((uint)local_8 | 0x40);
        }
        else {
          if (uVar3 == 0x6e) {
            piVar6 = (int *)ControlsUI__Helper_00562013(&param_3);
            if (((uint)local_8 & 0x20) == 0) {
              *piVar6 = local_18;
            }
            else {
              *(undefined2 *)piVar6 = (undefined2)local_18;
            }
            local_34 = 1;
            break;
          }
          if (uVar3 == 0x6f) {
            local_c = (byte *)0x8;
            if (((uint)local_8 & 0x80) != 0) {
              local_8 = (byte *)((uint)local_8 | 0x200);
            }
            goto LAB_00565568;
          }
          if (uVar3 == 0x70) {
            local_14 = 8;
            goto LAB_005654f7;
          }
          if (uVar3 == 0x73) {
LAB_00565288:
            iVar10 = local_14;
            if (local_14 == -1) {
              iVar10 = 0x7fffffff;
            }
            pbVar4 = (byte *)ControlsUI__Helper_00562013(&param_3);
            if (((uint)local_8 & 0x20) == 0) {
              if (pbVar4 == (byte *)0x0) {
                pbVar4 = PTR_DAT_00653764;
              }
              local_20 = 1;
              for (pbVar7 = pbVar4; (iVar10 != 0 && (*(short *)pbVar7 != 0)); pbVar7 = pbVar7 + 2) {
                iVar10 = iVar10 + -1;
              }
              local_c = (byte *)((int)pbVar7 - (int)pbVar4 >> 1);
            }
            else {
              if (pbVar4 == (byte *)0x0) {
                pbVar4 = PTR_DAT_00653760;
              }
              local_c = (byte *)0x0;
              pbVar7 = pbVar4;
              if (0 < iVar10) {
                do {
                  if (*pbVar7 == 0) break;
                  if ((PTR_DAT_00653890[(uint)*pbVar7 * 2 + 1] & 0x80) != 0) {
                    pbVar7 = pbVar7 + 1;
                  }
                  pbVar7 = pbVar7 + 1;
                  local_c = local_c + 1;
                } while ((int)local_c < iVar10);
              }
            }
            goto LAB_00565689;
          }
          if (uVar3 != 0x75) {
            if (uVar3 != 0x78) goto LAB_00565689;
            local_30 = 0x27;
            goto LAB_005654fa;
          }
        }
        local_c = (byte *)0xa;
LAB_00565568:
        if (((uint)local_8 & 0x8000) == 0) {
          if (((uint)local_8 & 0x20) == 0) {
            if (((uint)local_8 & 0x40) == 0) {
              uVar3 = ControlsUI__Helper_00562013(&param_3);
              iVar10 = 0;
              goto LAB_005655bb;
            }
            uVar3 = ControlsUI__Helper_00562013(&param_3);
          }
          else if (((uint)local_8 & 0x40) == 0) {
            uVar3 = ControlsUI__Helper_00562013(&param_3);
            uVar3 = uVar3 & 0xffff;
          }
          else {
            iVar10 = ControlsUI__Helper_00562013(&param_3);
            uVar3 = (uint)(short)iVar10;
          }
          iVar10 = (int)uVar3 >> 0x1f;
        }
        else {
          uVar3 = CRT__ReadIntAndAdvance8(&param_3);
          iVar10 = extraout_EDX;
        }
LAB_005655bb:
        if (((((uint)local_8 & 0x40) != 0) && (iVar10 < 1)) && (iVar10 < 0)) {
          bVar11 = uVar3 != 0;
          uVar3 = -uVar3;
          iVar10 = -(iVar10 + (uint)bVar11);
          local_8 = (byte *)((uint)local_8 | 0x100);
        }
        if (((uint)local_8 & 0x8000) == 0) {
          iVar10 = 0;
        }
        lVar12 = CONCAT44(iVar10,uVar3);
        if (local_14 < 0) {
          local_14 = 1;
        }
        else {
          local_8 = (byte *)((uint)local_8 & 0xfffffff7);
        }
        if (uVar3 == 0 && iVar10 == 0) {
          local_1c = 0;
        }
        local_10 = local_255;
        while ((iVar10 = local_14 + -1, 0 < local_14 || (lVar12 != 0))) {
          local_48 = (int)local_c >> 0x1f;
          local_4c = (int)local_c;
          local_14 = iVar10;
          iVar10 = __aullrem(lVar12,local_c,local_48);
          pbVar9 = (byte *)(iVar10 + 0x30);
          lVar12 = __aulldiv(lVar12,local_4c,local_48);
          if (0x39 < (int)pbVar9) {
            pbVar9 = pbVar9 + local_30;
          }
          pbVar4 = local_10 + -1;
          *local_10 = (byte)pbVar9;
          local_10 = pbVar4;
        }
        local_c = local_255 + -(int)local_10;
        pbVar4 = local_10 + 1;
        local_14 = iVar10;
        if ((((uint)local_8 & 0x200) != 0) && ((*pbVar4 != 0x30 || (local_c == (byte *)0x0)))) {
          local_c = local_255 + -(int)local_10 + 1;
          *local_10 = 0x30;
          pbVar4 = local_10;
        }
      }
LAB_00565689:
      local_10 = pbVar4;
      pbVar4 = local_8;
      if (local_34 == 0) {
        if (((uint)local_8 & 0x40) != 0) {
          if (((uint)local_8 & 0x100) == 0) {
            if (((uint)local_8 & 1) == 0) {
              if (((uint)local_8 & 2) == 0) goto LAB_005656c7;
              local_24 = 0x20;
            }
            else {
              local_24 = 0x2b;
            }
          }
          else {
            local_24 = 0x2d;
          }
          local_1c = 1;
        }
LAB_005656c7:
        iVar10 = (local_2c - local_1c) - (int)local_c;
        if (((uint)local_8 & 0xc) == 0) {
          ControlsUI__Helper_005657f0(0x20,iVar10,param_1,&local_18);
        }
        CRT__MapWideCharsWithCallbackStopOnError(&local_24,local_1c,param_1,&local_18);
        if ((((uint)pbVar4 & 8) != 0) && (((uint)pbVar4 & 4) == 0)) {
          ControlsUI__Helper_005657f0(0x30,iVar10,param_1,&local_18);
        }
        if ((local_20 == 0) && (0 < (int)local_c)) {
          pbVar9 = local_c + -1;
          pbVar7 = local_10;
          do {
            local_44 = CRT__MultiByteToWideChar_ThreadSafe((int)&local_40,(int)pbVar7,DAT_00653a9c);
            pbVar4 = pbVar9;
            if (local_44 < 1) break;
            ControlsUI__Helper_005657d0(local_40,param_1,&local_18);
            pbVar7 = pbVar7 + local_44;
            pbVar4 = pbVar9 + -1;
            bVar11 = 0 < (int)pbVar9;
            pbVar9 = pbVar4;
          } while (bVar11);
        }
        else {
          CRT__MapWideCharsWithCallbackStopOnError(local_10,(int)local_c,param_1,&local_18);
        }
        pbVar9 = pbVar4;
        if (((uint)local_8 & 4) != 0) {
          ControlsUI__Helper_005657f0(0x20,iVar10,param_1,&local_18);
        }
      }
    }
    sVar1 = *(short *)param_2;
    pbVar9 = (byte *)CONCAT22((short)((uint)pbVar9 >> 0x10),sVar1);
    pvVar2 = param_2;
  } while( true );
}
