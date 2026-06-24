/* address: 0x005286e0 */
/* name: CEngine__Unk_005286e0 */
/* signature: void __cdecl CEngine__Unk_005286e0(void * param_1) */


void __cdecl CEngine__Unk_005286e0(void *param_1)

{
  int iVar1;
  char cVar2;
  byte bVar3;
  bool bVar4;
  bool bVar5;
  undefined4 *puVar6;
  void *file;
  int extraout_EAX;
  int extraout_EAX_00;
  int extraout_EAX_01;
  int extraout_EAX_02;
  int iVar7;
  uint uVar8;
  char *pcVar9;
  bool bVar10;
  bool bVar11;
  int local_1a8;
  uint local_1a0;
  int local_19c;
  uint local_198;
  undefined4 local_194;
  char local_190;
  char local_18f [2];
  char acStack_18d [197];
  char local_c8 [200];

  iVar1 = DAT_008889f0 * 0x516c;
  file = fopen(param_1,&DAT_0064bdcc);
  if (file == (void *)0x0) {
    CConsole__Printf(&DAT_0066eb90,s_Couldn_t_open_CardID_file__0064bd24);
    return;
  }
  bVar3 = *(byte *)((int)file + 0xc);
  bVar11 = false;
  bVar10 = false;
  bVar4 = true;
  bVar5 = false;
  do {
    if ((bVar3 & 0x10) != 0) {
      fclose(file);
      return;
    }
    pcVar9 = local_18f;
    for (iVar7 = 0x31; iVar7 != 0; iVar7 = iVar7 + -1) {
      pcVar9[0] = '\0';
      pcVar9[1] = '\0';
      pcVar9[2] = '\0';
      pcVar9[3] = '\0';
      pcVar9 = pcVar9 + 4;
    }
    pcVar9[0] = '\0';
    pcVar9[1] = '\0';
    pcVar9[2] = '\0';
    local_190 = DAT_00662b2c;
    CDXTexture__Unk_0055fc5d(&local_190,199,file);
    if (local_190 == '/') {
      if (local_18f[0] != '/') {
LAB_0052879e:
        if (bVar11) {
          uVar8 = 0xffffffff;
          pcVar9 = s_Device__0064bdc4;
          do {
            if (uVar8 == 0) break;
            uVar8 = uVar8 - 1;
            cVar2 = *pcVar9;
            pcVar9 = pcVar9 + 1;
          } while (cVar2 != '\0');
          iVar7 = CDXTexture__Unk_0056e170(&local_190,s_Device__0064bdc4,(void *)(~uVar8 - 1));
          if (iVar7 != 0) goto LAB_00528848;
          uVar8 = 0xffffffff;
          pcVar9 = s_Device__0064bdc4;
          do {
            if (uVar8 == 0) break;
            uVar8 = uVar8 - 1;
            cVar2 = *pcVar9;
            pcVar9 = pcVar9 + 1;
          } while (cVar2 != '\0');
          CFastVB__Unk_0055e14f((void *)((int)&local_194 + ~uVar8 + 3),0x64bdc0);
          if (extraout_EAX != 1) goto LAB_00528848;
          if (((!bVar5) || (!bVar10)) &&
             (bVar10 = local_1a8 == *(int *)(&DAT_00855fe0 + iVar1), bVar10)) {
            CConsole__Printf(&DAT_0066eb90,s_Device_in_CardID___s_0064bda8);
          }
          bVar5 = true;
LAB_00528841:
          bVar4 = true;
        }
        else {
LAB_00528848:
          uVar8 = 0xffffffff;
          bVar5 = false;
          pcVar9 = s_Version__0064bd9c;
          do {
            if (uVar8 == 0) break;
            uVar8 = uVar8 - 1;
            cVar2 = *pcVar9;
            pcVar9 = pcVar9 + 1;
          } while (cVar2 != '\0');
          iVar7 = CDXTexture__Unk_0056e170(&local_190,s_Version__0064bd9c,(void *)(~uVar8 - 1));
          if (iVar7 == 0) {
            iVar7 = -1;
            pcVar9 = s_Version__0064bd9c;
            do {
              if (iVar7 == 0) break;
              iVar7 = iVar7 + -1;
              cVar2 = *pcVar9;
              pcVar9 = pcVar9 + 1;
            } while (cVar2 != '\0');
            CConsole__Printf(&DAT_0066eb90,s_CardID_version___s_0064bd88);
          }
          else {
            uVar8 = 0xffffffff;
            pcVar9 = s_Vendor__0064bd80;
            do {
              if (uVar8 == 0) break;
              uVar8 = uVar8 - 1;
              cVar2 = *pcVar9;
              pcVar9 = pcVar9 + 1;
            } while (cVar2 != '\0');
            iVar7 = CDXTexture__Unk_0056e170(&local_190,s_Vendor__0064bd80,(void *)(~uVar8 - 1));
            if (iVar7 == 0) {
              uVar8 = 0xffffffff;
              pcVar9 = s_Vendor__0064bd80;
              do {
                if (uVar8 == 0) break;
                uVar8 = uVar8 - 1;
                cVar2 = *pcVar9;
                pcVar9 = pcVar9 + 1;
              } while (cVar2 != '\0');
              CFastVB__Unk_0055e14f((void *)((int)&local_194 + ~uVar8 + 3),0x64bdc0);
              if (extraout_EAX_00 == 1) {
                bVar11 = local_1a8 == *(int *)(&DAT_00855fdc + iVar1);
                bVar4 = true;
                goto LAB_00528a65;
              }
            }
            if ((bVar11) && (bVar10)) {
              CFastVB__Unk_0055e14f(&local_190,0x64bd68);
              if (extraout_EAX_01 == 4) {
                iVar7 = *(int *)(&DAT_00855fd8 + iVar1);
                if (((local_19c < iVar7) ||
                    ((local_19c == iVar7 && (local_1a0 <= *(uint *)(&DAT_00855fd4 + iVar1))))) &&
                   ((iVar7 < local_194 ||
                    ((local_194 == iVar7 && (*(uint *)(&DAT_00855fd4 + iVar1) <= local_198))))))
                goto LAB_00528841;
                bVar4 = false;
              }
              else if (bVar4) {
                uVar8 = 0xffffffff;
                pcVar9 = &DAT_0064bd60;
                do {
                  if (uVar8 == 0) break;
                  uVar8 = uVar8 - 1;
                  cVar2 = *pcVar9;
                  pcVar9 = pcVar9 + 1;
                } while (cVar2 != '\0');
                iVar7 = CDXTexture__Unk_0056e170(&local_190,&DAT_0064bd60,(void *)(~uVar8 - 1));
                if (iVar7 == 0) {
                  uVar8 = 0xffffffff;
                  pcVar9 = &DAT_0064bd60;
                  do {
                    if (uVar8 == 0) break;
                    uVar8 = uVar8 - 1;
                    cVar2 = *pcVar9;
                    pcVar9 = pcVar9 + 1;
                  } while (cVar2 != '\0');
                  CFastVB__Unk_0055e14f((void *)((int)&local_194 + ~uVar8 + 3),0x64bd58);
                  puVar6 = DAT_0089c018;
                  if (extraout_EAX_02 == 2) {
                    for (; puVar6 != (undefined4 *)0x0; puVar6 = (undefined4 *)puVar6[1]) {
                      iVar7 = stricmp(local_c8,(char *)puVar6[2]);
                      if (iVar7 == 0) {
                        if (puVar6 != (undefined4 *)0x0) {
                          CConsole__Printf(&DAT_0066eb90,s_Setting_tweak__s_to__f_0064bd40);
                          (**(code **)*puVar6)();
                        }
                        break;
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    else if (((local_190 != '\0') && (local_190 != '\r')) && (local_190 != '\n')) goto LAB_0052879e;
LAB_00528a65:
    bVar3 = *(byte *)((int)file + 0xc);
  } while( true );
}
