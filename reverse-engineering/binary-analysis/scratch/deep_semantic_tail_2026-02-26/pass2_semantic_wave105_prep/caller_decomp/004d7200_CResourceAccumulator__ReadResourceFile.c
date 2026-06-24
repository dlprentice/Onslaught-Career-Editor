/* address: 0x004d7200 */
/* name: CResourceAccumulator__ReadResourceFile */
/* signature: undefined CResourceAccumulator__ReadResourceFile(void) */


void CResourceAccumulator__ReadResourceFile(int param_1,void *param_2,int param_3)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  char *pcVar6;
  int unaff_EDI;
  char *pcVar7;
  undefined8 uVar8;
  char *local_5cc;
  char local_5c5;
  undefined1 local_5c4;
  undefined1 local_5c3;
  undefined1 local_5c2;
  undefined1 local_5c1;
  undefined1 local_5c0;
  float local_5bc;
  undefined1 local_5b8 [4];
  undefined1 local_5b4 [4];
  char local_5b0 [64];
  char local_570 [100];
  char local_50c [256];
  char local_40c [256];
  char local_30c [256];
  char local_20c [256];
  char local_10c [256];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d48ef;
  local_c = ExceptionList;
  local_5c5 = param_2 != (void *)0x0;
  ExceptionList = &local_c;
  local_5bc = PLATFORM__GetSysTimeFloat();
  if (param_1 == -1) {
    CConsole__Status(&DAT_00663498,s_Loading_base_resources_00631c9c);
    pcVar2 = s_Loading_base_resources_00631c84;
  }
  else if (param_1 == -2) {
    CConsole__Status(&DAT_00663498,s_Loading_Frontend_resources_00631c68);
    pcVar2 = s_Loading_Frontend_resources_00631c4c;
  }
  else {
    if (param_1 == -3) {
      CConsole__Status(&DAT_00663498,s_Loading_loading_resources_00631c30);
      DebugTrace(s_Loading_loading_resources_00631c14);
      ExceptionList = local_c;
      return;
    }
    if (param_1 < 0) {
      CConsole__Status(&DAT_00663498,s_Loading_goodie_resources_00631bc4);
      pcVar2 = s_Loading_goodie_resources_00631ba8;
    }
    else {
      CConsole__Status(&DAT_00663498,s_Loading_level_resources_00631bfc);
      pcVar2 = s_Loading_level_resources_00631be0;
    }
  }
  DebugTrace(pcVar2);
  pcVar2 = (char *)OID__AllocObject(0x100,0x61,s_C__dev_ONSLAUGHT2_ResourceAccumu_00631b7c,0x300);
  local_5cc = pcVar2;
  CResourceAccumulator__GetResourceFilename(pcVar2,param_1);
  if (-1 < param_1) {
    uVar4 = 0xffffffff;
    do {
      pcVar6 = pcVar2;
      if (uVar4 == 0) break;
      uVar4 = uVar4 - 1;
      pcVar6 = pcVar2 + 1;
      cVar1 = *pcVar2;
      pcVar2 = pcVar6;
    } while (cVar1 != '\0');
    uVar4 = ~uVar4;
    pcVar6 = pcVar6 + -uVar4;
    pcVar7 = &DAT_0083cb08;
    for (uVar5 = uVar4 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
      *(undefined4 *)pcVar7 = *(undefined4 *)pcVar6;
      pcVar6 = pcVar6 + 4;
      pcVar7 = pcVar7 + 4;
    }
    for (uVar4 = uVar4 & 3; pcVar2 = local_5cc, uVar4 != 0; uVar4 = uVar4 - 1) {
      *pcVar7 = *pcVar6;
      pcVar6 = pcVar6 + 1;
      pcVar7 = pcVar7 + 1;
    }
  }
  local_5cc = (char *)OID__AllocObject(0x10,0x80,s_C__dev_ONSLAUGHT2_ResourceAccumu_00631b7c,0x330);
  pcVar6 = (char *)0x0;
  local_4 = 0;
  if (local_5cc != (char *)0x0) {
    pcVar6 = (char *)CChunker__Create();
  }
  local_4 = 0xffffffff;
  if (param_2 == (void *)0x0) {
    iVar3 = CUnitAI__Unk_004238c0(pcVar6,pcVar2,unaff_EDI);
    if (iVar3 == 0) {
      if (param_1 == -1) {
        pcVar7 = s_Loading_base_resources_00631c9c;
      }
      else if (param_1 == -2) {
        pcVar7 = s_Loading_Frontend_resources_00631c68;
      }
      else if (param_1 == -3) {
        pcVar7 = s_Loading_loading_resources_00631c30;
      }
      else if (param_1 < 0) {
        pcVar7 = s_Loading_goodie_resources_00631bc4;
      }
      else {
        pcVar7 = s_Loading_level_resources_00631bfc;
      }
      CConsole__StatusDone(&DAT_00663498,pcVar7,'\0');
      if (pcVar6 != (char *)0x0) {
        CUnitAI__Unk_00423840((int)pcVar6);
        OID__FreeObject(pcVar6);
      }
      goto LAB_004d79f4;
    }
  }
  else {
    CResourceAccumulator__Helper_00423870(pcVar6,param_2,unaff_EDI);
  }
  if (-1 < param_1) {
    DAT_006317cc = param_1;
  }
  uVar4 = CMeshPart__Helper_00423910((uint)pcVar6);
  while (uVar4 != 0) {
    if (uVar4 == ((DAT_00631b77 * 0x100 + (int)DAT_00631b76) * 0x100 + (int)DAT_00631b75) * 0x100 +
                 (int)DAT_00631b74) {
      CMeshPart__Helper_00423960(pcVar6,(int)local_5b4,4,1,unaff_EDI);
LAB_004d7940:
      CUnitAI__Unk_00423990(pcVar6);
    }
    else if (uVar4 == ((DAT_00631b6f * 0x100 + (int)DAT_00631b6e) * 0x100 + (int)DAT_00631b6d) *
                      0x100 + (int)DAT_00631b6c) {
      CMeshPart__Helper_00423960(pcVar6,(int)local_5b8,4,1,unaff_EDI);
    }
    else {
      if (uVar4 == ((DAT_00631b67 * 0x100 + (int)DAT_00631b66) * 0x100 + (int)DAT_00631b65) * 0x100
                   + (int)DAT_00631b64) {
        CMeshPart__Helper_00423960(pcVar6,(int)&local_5cc,4,1,unaff_EDI);
        if (local_5cc != DAT_006317dc) {
          sprintf(local_20c,s_Resource_file_does_not_match_cod_00631b08);
        }
        CMeshPart__Helper_00423960(pcVar6,(int)&local_5cc,4,1,unaff_EDI);
        if (local_5cc != DAT_006317e0) {
          sprintf(local_50c,s_Resource_file_does_not_match_cod_00631ab0);
        }
        CMeshPart__Helper_00423960(pcVar6,(int)&local_5cc,4,1,unaff_EDI);
        if (local_5cc != DAT_006317e4) {
          sprintf(local_40c,s_Resource_file_does_not_match_cod_00631a54);
        }
        CMeshPart__Helper_00423960(pcVar6,(int)&local_5cc,4,1,unaff_EDI);
        if (local_5cc != DAT_006317e8) {
          sprintf(local_30c,s_Resource_file_does_not_match_cod_006319f4);
        }
        CMeshPart__Helper_00423960(pcVar6,(int)&local_5cc,4,1,unaff_EDI);
        if (local_5cc != DAT_006317ec) {
          sprintf(local_10c,s_Resource_file_does_not_match_cod_00631994);
        }
        goto LAB_004d7940;
      }
      if (uVar4 == ((DAT_0062fad7 * 0x100 + (int)DAT_0062fad6) * 0x100 + (int)DAT_0062fad5) * 0x100
                   + (int)DAT_0062fad4) {
        CMesh__Deserialize(pcVar6);
      }
      else {
        if (param_3 != 0) goto LAB_004d7940;
        if (uVar4 == ((DAT_0063198f * 0x100 + (int)DAT_0063198e) * 0x100 + (int)DAT_0063198d) *
                     0x100 + (int)DAT_0063198c) {
          CDXTexture__Deserialize(0);
        }
        else if (uVar4 == ((DAT_00631987 * 0x100 + (int)DAT_00631986) * 0x100 + (int)DAT_00631985) *
                          0x100 + (int)DAT_00631984) {
          CResourceAccumulator__Helper_0044a6e0(pcVar6);
        }
        else if (uVar4 == ((DAT_0063197f * 0x100 + (int)DAT_0063197e) * 0x100 + (int)DAT_0063197d) *
                          0x100 + (int)DAT_0063197c) {
          CWorld__DeserializeWorld();
        }
        else if (uVar4 == ((DAT_00631977 * 0x100 + (int)DAT_00631976) * 0x100 + (int)DAT_00631975) *
                          0x100 + (int)DAT_00631974) {
          CDXImposter__Deserialize();
        }
        else {
          if (uVar4 == ((DAT_0063196f * 0x100 + (int)DAT_0063196e) * 0x100 + (int)DAT_0063196d) *
                       0x100 + (int)DAT_0063196c) goto LAB_004d7940;
          if (uVar4 == ((DAT_00631967 * 0x100 + (int)DAT_00631966) * 0x100 + (int)DAT_00631965) *
                       0x100 + (int)DAT_00631964) {
            CResourceAccumulator__InitVertexShaderPrograms(pcVar6);
          }
          else if (uVar4 == ((DAT_0063195f * 0x100 + (int)DAT_0063195e) * 0x100 + (int)DAT_0063195d)
                            * 0x100 + (int)DAT_0063195c) {
            PCPlatform__DeserializeFontsAndAssets(&DAT_0088a0a8,(int)pcVar6);
          }
          else if (uVar4 == ((DAT_00631957 * 0x100 + (int)DAT_00631956) * 0x100 + (int)DAT_00631955)
                            * 0x100 + (int)DAT_00631954) {
            CDXSurf__CreateSurfaceArray();
          }
          else if (uVar4 == ((DAT_0063194f * 0x100 + (int)DAT_0063194e) * 0x100 + (int)DAT_0063194d)
                            * 0x100 + (int)DAT_0063194c) {
            CStaticShadows__LoadAll();
          }
          else if (uVar4 == ((DAT_00631947 * 0x100 + (int)DAT_00631946) * 0x100 + (int)DAT_00631945)
                            * 0x100 + (int)DAT_00631944) {
            CDXPatch__LoadFromFile();
          }
          else if (uVar4 == ((DAT_0063193f * 0x100 + (int)DAT_0063193e) * 0x100 + (int)DAT_0063193d)
                            * 0x100 + (int)DAT_0063193c) {
            CDamage__CreateTextureBuffer();
          }
          else {
            if (uVar4 != ((DAT_00631937 * 0x100 + (int)DAT_00631936) * 0x100 + (int)DAT_00631935) *
                         0x100 + (int)DAT_00631934) {
              local_5c4 = (undefined1)uVar4;
              local_5c0 = 0;
              local_5c1 = (undefined1)(uVar4 >> 0x18);
              local_5c3 = (undefined1)(uVar4 >> 8);
              local_5c2 = (undefined1)(uVar4 >> 0x10);
              sprintf(local_5b0,s_Unknown_chunk_ID__s_in_resource_f_0063190c);
              DebugTrace(local_5b0);
              goto LAB_004d7940;
            }
            CFEPGoodies__Deserialise(&DAT_008a0f34,pcVar6);
          }
        }
      }
    }
    if (local_5c5 == '\0') {
      CConsole__SetLoadingFraction(&DAT_00663498,0.0);
    }
    uVar4 = CMeshPart__Helper_00423910((uint)pcVar6);
  }
  CUnitAI__Unk_00423900();
  if (param_1 == -1) {
    uVar8 = 0x100631c9c;
  }
  else if (param_1 == -2) {
    uVar8 = 0x100631c68;
  }
  else if (param_1 == -3) {
    uVar8 = 0x100631c30;
  }
  else {
    uVar8 = 0x100631bfc;
  }
  CConsole__StatusDone(&DAT_00663498,(char *)uVar8,(char)((ulonglong)uVar8 >> 0x20));
  OID__FreeObject(pcVar2);
  PLATFORM__GetSysTimeFloat();
  sprintf(local_570,s_CResourceAccumulator__ReadResour_006318d4);
  DebugTrace(local_570);
  if (pcVar6 == (char *)0x0) {
    ExceptionList = local_c;
    return;
  }
  CUnitAI__Unk_00423840((int)pcVar6);
  pcVar2 = pcVar6;
LAB_004d79f4:
  OID__FreeObject(pcVar2);
  ExceptionList = local_c;
  return;
}
