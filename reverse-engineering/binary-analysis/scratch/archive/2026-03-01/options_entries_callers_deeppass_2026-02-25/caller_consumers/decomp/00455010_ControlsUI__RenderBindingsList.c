/* address: 0x00455010 */
/* name: ControlsUI__RenderBindingsList */
/* signature: undefined ControlsUI__RenderBindingsList(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
ControlsUI__RenderBindingsList(int param_1,int param_2,undefined4 param_3,float param_4,int param_5)

{
  char cVar1;
  short sVar2;
  bool bVar3;
  wchar_t *pwVar4;
  int *piVar5;
  int iVar6;
  short *psVar7;
  void *pvVar8;
  uint uVar9;
  float scale_y;
  int iVar10;
  uint uVar11;
  int iVar12;
  int unaff_EDI;
  undefined4 *puVar13;
  char *pcVar14;
  float10 extraout_ST0;
  float10 fVar15;
  float x;
  float y;
  float z;
  float scale_x;
  short *text;
  float transition;
  void *local_71c;
  float local_718;
  int iStack_70c;
  int local_704;
  int local_700;
  float local_6fc;
  uint uStack_6f8;
  undefined4 local_6f4;
  uint uStack_6f0;
  undefined4 uStack_6ec;
  uint uStack_6e8;
  undefined4 local_6e4;
  uint local_6e0;
  undefined4 uStack_6dc;
  CHAR local_6d8 [40];
  short local_6b0;
  undefined4 local_6ae [149];
  undefined1 local_458 [40];
  undefined4 local_430;
  undefined4 local_42c;
  undefined4 local_428;
  undefined4 local_424;
  undefined4 local_218;
  undefined4 local_214;
  undefined4 local_210;
  undefined4 local_20c;

  local_718 = param_4;
  D3DStateCache__SetState114Raw(0,6,1);
  D3DStateCache__SetState114Raw(0,5,1);
  iVar12 = *(int *)(param_1 + 0x20);
  if (iVar12 < 0x16) {
    local_6fc = param_4 + _DAT_005d85f4;
    do {
      if (local_6fc <= local_718) break;
      local_6b0 = DAT_00677d78;
      puVar13 = local_6ae;
      for (iVar10 = 0x95; iVar10 != 0; iVar10 = iVar10 + -1) {
        *puVar13 = 0;
        puVar13 = puVar13 + 1;
      }
      uVar11 = 0xff7f7f7f;
      *(undefined2 *)puVar13 = 0;
      bVar3 = false;
      iVar10 = iVar12 + 0x37;
      switch(iVar12) {
      case -0x36:
      case 0:
      case 3:
      case 8:
      case 0xd:
      case 0x10:
switchD_004550c4_caseD_ffffffca:
        if (iVar10 == 0x37) {
          if (param_2 == 0) {
            iVar10 = 0x33;
          }
          else if (param_2 == 2) {
            iVar10 = 0x34;
          }
LAB_00455a51:
          pwVar4 = Localization__GetStringById(iVar10);
LAB_00455a5f:
          CTexture__Unk_0055e64e(&local_6b0,pwVar4);
          goto switchD_004551e0_caseD_3;
        }
        if (param_2 == 1) goto LAB_00455a51;
        break;
      default:
        if (param_2 == 1) goto switchD_004550c4_caseD_ffffffca;
        if (iVar10 == 0x38) {
          if ((&CAREER_mInvertYWalker_P1)[param_2 / 2] != 0) {
            pwVar4 = Localization__GetStringById(0x36);
            goto LAB_00455a5f;
          }
          iVar10 = 0x35;
          goto LAB_00455a51;
        }
        if (iVar10 == 0x39) {
          if ((&CAREER_mInvertYFlight_P1)[param_2 / 2] == 0) {
            pwVar4 = Localization__GetStringById(0x35);
          }
          else {
            pwVar4 = Localization__GetStringById(0x36);
          }
          goto LAB_00455a5f;
        }
        if (((g_ControlRemapActionCode == iVar10) && (param_2 / 2 == g_ControlRemapSlotIndex)) &&
           (g_ControlRemapActive == '\0')) {
          bVar3 = true;
          CTexture__Unk_0055e64e(&local_6b0,u________00629124);
          goto switchD_004551e0_caseD_3;
        }
        Controls__DispatchRemap(iVar10,0,&LAB_00456060);
        piVar5 = OptionsEntries__FindById(g_ControlRemapCurrentEntryId);
        piVar5 = piVar5 + (param_2 / 2) * 3 + 2;
        if ((piVar5 == (int *)0x0) || (iVar10 = *piVar5, iVar10 == -1)) {
          iVar10 = 0x78;
LAB_00455a13:
          pwVar4 = Localization__GetStringById(iVar10);
          CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
        }
        else {
          iVar6 = piVar5[1];
          switch(iVar6) {
          case 0:
          case 1:
          case 2:
            if ((iVar10 < 0) || (DAT_00888ff8 <= iVar10)) {
              pwVar4 = Localization__GetStringById(0x57);
            }
            else {
              local_430 = 0x218;
              local_42c = 0x10;
              local_428 = 0;
              local_424 = 0;
              pwVar4 = Localization__GetStringById(iVar10 + 0x58);
            }
            CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
            CDXTexture__Unk_0055e598(local_458,0x629110);
            CDXTexture__Unk_0055e624(&local_6b0,local_458);
            break;
          case 4:
          case 5:
          case 6:
          case 7:
            if (iVar6 == 6) {
              iVar6 = 4;
            }
            else if (iVar6 == 7) {
              iVar6 = 5;
            }
            if ((iVar10 < 0) || (DAT_00888ff8 <= iVar10)) {
              pwVar4 = Localization__GetStringById(0x5d);
            }
            else {
              local_218 = 0x218;
              local_214 = 0x10;
              local_210 = 0;
              local_20c = 0;
              pwVar4 = Localization__GetStringById(iVar10 + 0x5e);
            }
            CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
            CDXTexture__Unk_0055e624(&local_6b0,&DAT_00629120);
            if (iVar6 == 4) {
              sVar2 = (short)piVar5[2];
              if (sVar2 == -1) {
                iVar10 = 0x66;
                goto LAB_00455a13;
              }
              if (sVar2 == -2) {
                pwVar4 = Localization__GetStringById(0x68);
                CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              }
              else if (sVar2 == -3) {
                pwVar4 = Localization__GetStringById(0x6a);
                CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              }
              else {
                if (sVar2 == -4) {
                  iVar10 = 0x6c;
                  goto LAB_00455a13;
                }
                if (sVar2 == -5) {
                  pwVar4 = Localization__GetStringById(0x6e);
                  CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
                }
                else if (sVar2 == -6) {
                  pwVar4 = Localization__GetStringById(0x70);
                  CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
                }
              }
            }
            else if (iVar6 == 5) {
              sVar2 = (short)piVar5[2];
              if (sVar2 == -1) {
                pwVar4 = Localization__GetStringById(0x67);
                CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              }
              else {
                if (sVar2 == -2) {
                  iVar10 = 0x69;
                  goto LAB_00455a13;
                }
                if (sVar2 == -3) {
                  pwVar4 = Localization__GetStringById(0x6b);
                  CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
                }
                else if (sVar2 == -4) {
                  pwVar4 = Localization__GetStringById(0x6d);
                  CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
                }
                else {
                  if (sVar2 == -5) {
                    iVar10 = 0x6f;
                    goto LAB_00455a13;
                  }
                  if (sVar2 == -6) {
                    pwVar4 = Localization__GetStringById(0x71);
                    CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
                  }
                }
              }
            }
            break;
          case 8:
          case 9:
          case 10:
            sVar2 = *(short *)((int)piVar5 + 10);
            iVar10 = piVar5[2];
            iVar6 = GetKeyNameTextA((int)(short)iVar10 << 0x10,local_6d8,0x28);
            if (iVar6 == 0) {
              switch((int)(short)iVar10) {
              case 1:
                pwVar4 = Localization__GetStringById(0x7d);
                break;
              default:
                pwVar4 = Localization__GetStringById(0x51);
                CTexture__Unk_0055e64e(&DAT_00677880,pwVar4);
                CDXTexture__Unk_0055e624(&DAT_00677880,&DAT_00629118);
                if (sVar2 == 0) {
                  iVar10 = WcsLen((short *)&DAT_00677880);
                  *(undefined2 *)((int)&g_ControlRemapCurrentEntryId + iVar10 * 2 + 2) = 0x3f;
                }
                else {
                  iVar10 = WcsLen((short *)&DAT_00677880);
                  *(short *)((int)&g_ControlRemapCurrentEntryId + iVar10 * 2 + 2) = sVar2;
                }
                goto LAB_004556f2;
              case 0xe:
                pwVar4 = Localization__GetStringById(0x7e);
                break;
              case 0xf:
                pwVar4 = Localization__GetStringById(0x7f);
                break;
              case 0x1c:
                pwVar4 = Localization__GetStringById(0x80);
                break;
              case 0x1d:
                pwVar4 = Localization__GetStringById(0x81);
                break;
              case 0x27:
                pwVar4 = Localization__GetStringById(0x83);
                break;
              case 0x28:
                pwVar4 = Localization__GetStringById(0x84);
                break;
              case 0x29:
                pwVar4 = Localization__GetStringById(0x85);
                break;
              case 0x2a:
                pwVar4 = Localization__GetStringById(0x86);
                break;
              case 0x36:
                pwVar4 = Localization__GetStringById(0x87);
                break;
              case 0x37:
                pwVar4 = Localization__GetStringById(0xa6);
                break;
              case 0x38:
                pwVar4 = Localization__GetStringById(0x88);
                break;
              case 0x39:
                pwVar4 = Localization__GetStringById(0x89);
                break;
              case 0x3a:
                pwVar4 = Localization__GetStringById(0x82);
                break;
              case 0x3b:
                pwVar4 = Localization__GetStringById(0x8c);
                break;
              case 0x3c:
                pwVar4 = Localization__GetStringById(0x8d);
                break;
              case 0x3d:
                pwVar4 = Localization__GetStringById(0x8e);
                break;
              case 0x3e:
                pwVar4 = Localization__GetStringById(0x8f);
                break;
              case 0x3f:
                pwVar4 = Localization__GetStringById(0x90);
                break;
              case 0x40:
                pwVar4 = Localization__GetStringById(0x91);
                break;
              case 0x41:
                pwVar4 = Localization__GetStringById(0x92);
                break;
              case 0x42:
                pwVar4 = Localization__GetStringById(0x93);
                break;
              case 0x43:
                pwVar4 = Localization__GetStringById(0x94);
                break;
              case 0x44:
                pwVar4 = Localization__GetStringById(0x95);
                break;
              case 0x45:
                pwVar4 = Localization__GetStringById(0x7c);
                break;
              case 0x46:
                pwVar4 = Localization__GetStringById(0x99);
                break;
              case 0x47:
                pwVar4 = Localization__GetStringById(0xa8);
                break;
              case 0x48:
                pwVar4 = Localization__GetStringById(0xa9);
                break;
              case 0x49:
                pwVar4 = Localization__GetStringById(0xaa);
                break;
              case 0x4a:
                pwVar4 = Localization__GetStringById(0xa7);
                break;
              case 0x4b:
                pwVar4 = Localization__GetStringById(0xac);
                break;
              case 0x4c:
                pwVar4 = Localization__GetStringById(0xad);
                break;
              case 0x4d:
                pwVar4 = Localization__GetStringById(0xae);
                break;
              case 0x4e:
                pwVar4 = Localization__GetStringById(0xab);
                break;
              case 0x4f:
                pwVar4 = Localization__GetStringById(0xaf);
                break;
              case 0x50:
                pwVar4 = Localization__GetStringById(0xb0);
                break;
              case 0x51:
                pwVar4 = Localization__GetStringById(0xb1);
                break;
              case 0x52:
                pwVar4 = Localization__GetStringById(0xb3);
                break;
              case 0x53:
                pwVar4 = Localization__GetStringById(0xb4);
                break;
              case 0x57:
                pwVar4 = Localization__GetStringById(0x96);
                break;
              case 0x58:
                pwVar4 = Localization__GetStringById(0x97);
                break;
              case 0x9c:
                pwVar4 = Localization__GetStringById(0xb2);
                break;
              case 0x9d:
                pwVar4 = Localization__GetStringById(0x8b);
                break;
              case 0xb5:
                pwVar4 = Localization__GetStringById(0xa5);
                break;
              case 0xb7:
                pwVar4 = Localization__GetStringById(0x98);
                break;
              case 0xb8:
                pwVar4 = Localization__GetStringById(0x8a);
                break;
              case 0xc5:
                pwVar4 = Localization__GetStringById(0xa4);
                break;
              case 199:
                pwVar4 = Localization__GetStringById(0x9b);
                break;
              case 200:
                pwVar4 = Localization__GetStringById(0xa1);
                break;
              case 0xc9:
                pwVar4 = Localization__GetStringById(0x9c);
                break;
              case 0xcb:
                pwVar4 = Localization__GetStringById(0xa0);
                break;
              case 0xcd:
                pwVar4 = Localization__GetStringById(0xa2);
                break;
              case 0xcf:
                pwVar4 = Localization__GetStringById(0x9e);
                break;
              case 0xd0:
                pwVar4 = Localization__GetStringById(0xa3);
                break;
              case 0xd1:
                pwVar4 = Localization__GetStringById(0x9f);
                break;
              case 0xd2:
                pwVar4 = Localization__GetStringById(0x9a);
                break;
              case 0xd3:
                pwVar4 = Localization__GetStringById(0x9d);
                break;
              case 0xdb:
                pwVar4 = Localization__GetStringById(0x7b);
                break;
              case 0xdc:
                pwVar4 = Localization__GetStringById(0x7a);
                break;
              case 0xdd:
                pwVar4 = Localization__GetStringById(0x79);
              }
            }
            else {
              iVar10 = -1;
              pcVar14 = local_6d8;
              do {
                if (iVar10 == 0) break;
                iVar10 = iVar10 + -1;
                cVar1 = *pcVar14;
                pcVar14 = pcVar14 + 1;
              } while (cVar1 != '\0');
              if (iVar10 == -3) {
                pwVar4 = Localization__GetStringById(0x51);
                CTexture__Unk_0055e64e(&DAT_00677880,pwVar4);
                CDXTexture__Unk_0055e624(&DAT_00677880,&DAT_00629120);
                psVar7 = Text__AsciiToWideScratch(local_6d8);
                CDXTexture__Unk_0055e624(&DAT_00677880,psVar7);
LAB_004556f2:
                pwVar4 = (wchar_t *)&DAT_00677880;
              }
              else {
                pwVar4 = Text__AsciiToWideScratch(local_6d8);
              }
            }
            CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
            break;
          case 0xb:
          case 0xc:
            pwVar4 = Localization__GetStringById(0x52);
            CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
            break;
          case 0xd:
          case 0xe:
            iVar10 = 0x53;
            goto LAB_00455a13;
          case 0xf:
          case 0x10:
          case 0x11:
            switch((short)piVar5[2]) {
            case 0:
              pwVar4 = Localization__GetStringById(0x54);
              CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              break;
            case 1:
              pwVar4 = Localization__GetStringById(0x55);
              CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              break;
            case 2:
              pwVar4 = Localization__GetStringById(0x56);
              CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              break;
            case 3:
              pwVar4 = Localization__GetStringById(0x73);
              CDXTexture__Unk_0055e624(&local_6b0,pwVar4);
              break;
            case 4:
              iVar10 = 0x72;
              goto LAB_00455a13;
            }
          }
        }
switchD_004551e0_caseD_3:
        piVar5 = &local_704;
        psVar7 = &local_6b0;
        pvVar8 = CPlatform__Font(&DAT_0088a0a8,2);
        CDXFont__GetTextExtent(pvVar8,psVar7,piVar5);
        if (param_2 == 0) {
          local_71c = (void *)0x42480000;
        }
        else if (param_2 == 1) {
          local_71c = (void *)(_DAT_005db3e8 - (float)local_704 * _DAT_005d85ec);
        }
        else if (param_2 == 2) {
          local_71c = (void *)(_DAT_005db494 - (float)local_704);
        }
        switch(iVar12) {
        case -0x36:
        case 0:
        case 3:
        case 8:
        case 0xd:
        case 0x10:
switchD_00455ada_caseD_ffffffca:
          uVar11 = 0xff3f7f2f;
          break;
        default:
          if (param_2 == 1) goto switchD_00455ada_caseD_ffffffca;
          if (param_5 != 0) {
            if ((g_ControlRemapActive != '\0') &&
               (iVar10 = CVBufTexture__Unk_00523b50
                                   ((float)local_71c,local_718,(float)local_704 + (float)local_71c,
                                    (float)local_700 + local_718), (char)iVar10 != '\0')) {
              *(int *)(param_1 + 0x28) = iVar12;
              *(int *)(param_1 + 0x24) = param_2 / 2;
            }
            if ((g_ControlRemapActive != '\0') &&
               (uVar9 = CVBufTexture__Unk_00523cc0
                                  ((float)local_71c,local_718,(float)local_704 + (float)local_71c,
                                   (float)local_700 + local_718), (char)uVar9 != '\0')) {
              *(int *)(param_1 + 0x24) = param_2 / 2;
              *(int *)(param_1 + 0x28) = iVar12;
              Controls__BeginRemapCapture();
            }
          }
          if (((iVar12 == *(int *)(param_1 + 0x28)) && (param_2 / 2 == *(int *)(param_1 + 0x24))) &&
             (param_5 != 0)) {
            uVar11 = 0xff7f6f2f;
          }
        }
        if (bVar3) {
          PLATFORM__GetSysTimeFloat();
          CDXTexture__Unk_0055e3ea();
          DAT_00640054._0_1_ = 0;
          fVar15 = (float10)fcos(extraout_ST0 * (float10)_DAT_005d85e0);
          iStack_70c = (int)(longlong)
                            ROUND((fVar15 + (float10)_DAT_005d8568) * (float10)_DAT_005d85ec *
                                  (float10)_DAT_005d8c70);
          scale_y = (float)(((uVar11 >> 8 & 0xffff0000) * iStack_70c ^ uVar11) & 0xffffff ^
                           (uVar11 >> 8 & 0xff0000) * iStack_70c);
        }
        else {
          scale_y = (float)(((uVar11 >> 8 & 0xffff0000) * 0xff ^ uVar11) & 0xffffff ^
                           (uVar11 >> 8 & 0xff0000) * 0xff);
        }
        if ((g_ControlRemapActive == '\0') && (!bVar3)) {
          local_6e0 = (uint)scale_y >> 0x18;
          uStack_6dc = 0;
          local_6f4 = 0;
          uStack_6f8 = (uint)scale_y >> 0x10 & 0xff;
          local_6e4 = 0;
          uStack_6ec = 0;
          iStack_70c = (int)(longlong)ROUND((float)local_6e0 * _DAT_005d8df8);
          iVar10 = iStack_70c * 0x100;
          iStack_70c = (int)(longlong)ROUND((float)uStack_6f8 * _DAT_005d8df8);
          iVar10 = iVar10 + iStack_70c;
          uStack_6e8 = (uint)scale_y >> 8 & 0xff;
          uStack_6f0 = (uint)scale_y & 0xff;
          iStack_70c = (int)(longlong)ROUND((float)uStack_6e8 * _DAT_005d8df8);
          iVar10 = iVar10 * 0x100 + iStack_70c;
          iStack_70c = (int)(longlong)ROUND((float)uStack_6f0 * _DAT_005d85ec);
          scale_y = (float)(iStack_70c + iVar10 * -0x100);
        }
        iVar10 = 0;
        transition = 0.0;
        psVar7 = &local_6b0;
        text = (short *)0x447a0000;
        scale_x = 1.0;
        z = 1.0;
        y = 0.32;
        pvVar8 = local_71c;
        x = local_718;
        CPlatform__Font(&DAT_0088a0a8,2);
        CDXFont__DrawTextDynamic
                  (pvVar8,x,y,z,scale_x,scale_y,(int)psVar7,text,transition,iVar10,unaff_EDI);
      }
      local_718 = local_718 + _DAT_005d85cc;
      iVar12 = iVar12 + 1;
    } while (iVar12 < 0x16);
  }
  D3DStateCache__SetState114Raw(0,6,2);
  D3DStateCache__SetState114Raw(0,5,2);
  return;
}
