/* address: 0x00559410 */
/* name: CDXTexture__CreateMipmaps */
/* signature: undefined CDXTexture__CreateMipmaps(void) */


void __thiscall CDXTexture__CreateMipmaps(uint *param_1,uint *param_2,int param_3,int param_4)

{
  uint *arg8;
  uint uVar1;
  int iVar2;
  int extraout_EAX;
  void *pvVar3;
  uint *puVar4;
  uint *puVar5;
  uint arg3;
  uint uVar6;
  uint uVar7;
  uint *puVar8;
  uint *puVar9;
  uint unaff_EBP;
  undefined4 *arg2;
  uint uVar10;
  byte bVar11;
  uint unaff_ESI;
  uint *puVar12;
  int iVar13;
  uint *puVar14;
  int *piVar15;
  uint uVar16;
  uint uStack_68;
  undefined2 local_64;
  uint uStack_58;
  uint uStack_54;
  int iStack_50;
  uint *local_4c;
  int iStack_3c;
  uint *puStack_38;
  undefined1 auStack_28 [8];
  _MEMORYSTATUS local_20;

  arg3 = (uint)(short)param_1[0x2c];
  arg2 = (undefined4 *)param_1[0x2b];
  uVar1 = param_1[0x51];
  iVar13 = param_4;
  while ((DAT_00888aac < arg2 || (DAT_00888ab0 < arg3))) {
    arg2 = (undefined4 *)((uint)arg2 >> 1);
    arg3 = arg3 >> 1;
    if (1 < iVar13) {
      iVar13 = iVar13 + -1;
    }
    if (1 < (int)param_1[0x52]) {
      param_1[0x52] = param_1[0x52] - 1;
    }
    *(short *)((int)param_1 + 0xb2) = *(short *)((int)param_1 + 0xb2) + 1;
  }
  DebugTrace(s______________lose_res_texture____00652904);
  switch(uVar1) {
  default:
    iVar2 = 0;
    break;
  case 1:
    iVar2 = 0x19;
    break;
  case 2:
    iVar2 = 0x1a;
    break;
  case 3:
    iVar2 = 0x16;
    break;
  case 4:
    iVar2 = 0x15;
    break;
  case 5:
    iVar2 = 0x17;
    break;
  case 6:
    iVar2 = 0x31545844;
    break;
  case 7:
    iVar2 = 0x32545844;
    break;
  case 8:
    iVar2 = 0x34545844;
    break;
  case 9:
    iVar2 = 0x3c;
    break;
  case 10:
    iVar2 = 0x3f;
  }
  arg8 = param_1 + param_3 + 0x2e;
  CEngine__CreateTextureUnchecked
            (&DAT_00855bb0,(int)arg2,arg3,iVar13,0,iVar2,param_1[0x54],(int)arg8);
  if (-1 < extraout_EAX) {
    GlobalMemoryStatus(&local_20);
    while ((1 < param_4 &&
           ((arg2 < (undefined4 *)param_1[0x2b] || (arg3 < (uint)(int)(short)param_1[0x2c]))))) {
      CMeshPart__Helper_00423910((uint)param_2);
      CUnitAI__Unk_00423990(param_2);
      *(short *)(param_1 + 0x2c) = (short)param_1[0x2c] >> 1;
      param_4 = param_4 + -1;
      param_1[0x2b] = (int)param_1[0x2b] >> 1;
    }
    uVar10 = param_1[0x2b];
    iStack_50 = 0;
    uStack_68 = arg3;
    local_4c = param_1;
    if (0 < param_4) {
      do {
        CMeshPart__Helper_00423910((uint)param_2);
        piVar15 = (int *)*arg8;
        uVar16 = 0;
        iVar13 = (**(code **)(*piVar15 + 0x4c))(piVar15,iStack_50,auStack_28,0);
        if (iVar13 < 0) {
          return;
        }
        bVar11 = 0;
        uVar6 = local_20.dwAvailPageFile;
        while (uVar6 < uVar10) {
          bVar11 = bVar11 + 1;
          uVar6 = local_20.dwAvailPageFile << (bVar11 & 0x1f);
        }
        uVar6 = local_4c[0x51];
        if ((uVar6 == 4) && (unaff_EBP == 2)) {
          pvVar3 = (void *)OID__AllocObject(*param_2 & 0xfffffffc,0x62,
                                            s_C__dev_ONSLAUGHT2_DXTexture_cpp_0065269c,0xb7a);
          CMeshPart__Helper_00423960(param_2,(int)pvVar3,*param_2,1,(int)piVar15);
          uVar6 = 0;
          if (uVar16 != 0) {
            do {
              uVar7 = 0;
              if (local_20.dwAvailPageFile != 0) {
                iVar13 = (uVar6 << (bVar11 & 0x1f)) * uVar10;
                do {
                  uVar10 = *(uint *)((int)pvVar3 + ((uVar7 << (bVar11 & 0x1f)) + iVar13) * 4);
                  iVar2 = (iStack_3c * uVar6 >> 1) + uVar7;
                  uVar7 = uVar7 + 1;
                  *(ushort *)((int)puStack_38 + iVar2 * 2) =
                       ((ushort)(uVar10 >> 0x10) & 0xf000) + ((ushort)(uVar10 >> 0xc) & 0xf00) +
                       ((ushort)(uVar10 >> 8) & 0xf0) + ((ushort)(uVar10 >> 4) & 0xf);
                  uVar10 = unaff_ESI;
                } while (uVar7 < local_20.dwAvailPageFile);
              }
              uVar6 = uVar6 + 1;
              param_2 = (uint *)local_20.dwTotalPageFile;
            } while (uVar6 < uVar16);
          }
          OID__FreeObject(pvVar3);
        }
        else if ((uVar6 == 3) && (unaff_EBP == 5)) {
          pvVar3 = (void *)OID__AllocObject(*param_2 & 0xfffffffc,0x62,
                                            s_C__dev_ONSLAUGHT2_DXTexture_cpp_0065269c,0xb92);
          CMeshPart__Helper_00423960(param_2,(int)pvVar3,*param_2,1,(int)piVar15);
          uVar6 = 0;
          if (uVar16 != 0) {
            do {
              uVar7 = 0;
              if (local_20.dwAvailPageFile != 0) {
                iVar13 = (uVar6 << (bVar11 & 0x1f)) * uVar10;
                do {
                  uVar10 = *(uint *)((int)pvVar3 + ((uVar7 << (bVar11 & 0x1f)) + iVar13) * 4);
                  iVar2 = (uVar6 * iStack_3c >> 1) + uVar7;
                  uVar7 = uVar7 + 1;
                  *(ushort *)((int)puStack_38 + iVar2 * 2) =
                       ((ushort)(uVar10 >> 8) & 0xf800) + ((ushort)(uVar10 >> 5) & 0x7e0) +
                       ((ushort)(uVar10 >> 3) & 0x1f);
                  uVar10 = unaff_ESI;
                } while (uVar7 < local_20.dwAvailPageFile);
              }
              uVar6 = uVar6 + 1;
              param_2 = (uint *)local_20.dwTotalPageFile;
            } while (uVar6 < uVar16);
          }
          OID__FreeObject(pvVar3);
        }
        else if (uVar6 == unaff_EBP) {
          uVar7 = 2;
          switch(uVar6) {
          case 1:
          case 2:
          case 5:
            uVar7 = 2;
            break;
          case 3:
          case 4:
            uVar7 = 4;
          }
          local_4c = (uint *)OID__AllocObject(*param_2,0x62,
                                              s_C__dev_ONSLAUGHT2_DXTexture_cpp_0065269c,0xbbf);
          CMeshPart__Helper_00423960(param_2,(int)local_4c,*param_2,1,(int)piVar15);
          if (local_20.dwAvailPageFile == uVar10) {
            if (uVar16 != 0) {
              uVar7 = uVar7 * uVar10;
              puVar4 = local_4c;
              puVar8 = puStack_38;
              do {
                puVar5 = puVar4;
                puVar9 = puVar8;
                for (uVar6 = uVar7 >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
                  *puVar9 = *puVar5;
                  puVar5 = puVar5 + 1;
                  puVar9 = puVar9 + 1;
                }
                for (uVar6 = uVar7 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
                  *(char *)puVar9 = (char)*puVar5;
                  puVar5 = (uint *)((int)puVar5 + 1);
                  puVar9 = (uint *)((int)puVar9 + 1);
                }
                puVar4 = (uint *)((int)puVar4 + uVar7);
                puVar8 = (uint *)((int)puVar8 + iStack_3c);
                uVar16 = uVar16 - 1;
                param_2 = (uint *)local_20.dwTotalPageFile;
              } while (uVar16 != 0);
            }
          }
          else {
            puVar4 = local_4c;
            puVar8 = puStack_38;
            if (((local_20.dwAvailPageFile == (int)uVar10 >> 1) && (uVar16 == (int)uStack_68 >> 1))
               && ((*(int *)(uVar10 + 0x144) == 3 || (*(int *)(uVar10 + 0x144) == 4)))) {
              for (; param_2 = (uint *)local_20.dwTotalPageFile, uVar16 != 0; uVar16 = uVar16 - 1) {
                if (local_20.dwAvailPageFile != 0) {
                  iVar13 = uVar10 * 4 << (bVar11 & 0x1f);
                  uStack_58 = local_20.dwAvailPageFile;
                  puVar5 = puVar4;
                  puVar9 = puVar8;
                  do {
                    *puVar9 = (*(uint *)(iVar13 + 4 + (int)puVar5) >> 2 & 0x3f3f3f3f) +
                              (puVar5[1] >> 2 & 0x3f3f3f3f) +
                              (*(uint *)(iVar13 + (int)puVar5) >> 2 & 0x3f3f3f3f) +
                              (*puVar5 >> 2 & 0x3f3f3f3f);
                    puVar5 = (uint *)((int)puVar5 + (uVar7 << (bVar11 & 0x1f)));
                    puVar9 = (uint *)((int)puVar9 + uVar7);
                    uStack_58 = uStack_58 - 1;
                    uVar10 = unaff_ESI;
                  } while (uStack_58 != 0);
                }
                puVar4 = (uint *)((uVar7 * uVar10 << (bVar11 & 0x1f)) + (int)puVar4);
                puVar8 = (uint *)(iStack_3c + (int)puVar8);
              }
            }
            else {
              for (; param_2 = (uint *)local_20.dwTotalPageFile, uVar16 != 0; uVar16 = uVar16 - 1) {
                if (local_20.dwAvailPageFile != 0) {
                  uStack_54 = local_20.dwAvailPageFile;
                  puVar5 = puVar4;
                  puVar9 = puVar8;
                  do {
                    puVar12 = puVar5;
                    puVar14 = puVar9;
                    for (uVar10 = uVar7 >> 2; uVar10 != 0; uVar10 = uVar10 - 1) {
                      *puVar14 = *puVar12;
                      puVar12 = puVar12 + 1;
                      puVar14 = puVar14 + 1;
                    }
                    puVar9 = (uint *)((int)puVar9 + uVar7);
                    for (uVar10 = uVar7 & 3; uVar10 != 0; uVar10 = uVar10 - 1) {
                      *(char *)puVar14 = (char)*puVar12;
                      puVar12 = (uint *)((int)puVar12 + 1);
                      puVar14 = (uint *)((int)puVar14 + 1);
                    }
                    puVar5 = (uint *)((int)puVar5 + (uVar7 << (bVar11 & 0x1f)));
                    uStack_54 = uStack_54 - 1;
                    uVar10 = unaff_ESI;
                  } while (uStack_54 != 0);
                }
                puVar4 = (uint *)((uVar7 * uVar10 << (bVar11 & 0x1f)) + (int)puVar4);
                puVar8 = (uint *)(iStack_3c + (int)puVar8);
              }
            }
          }
          OID__FreeObject(local_4c);
        }
        else {
          FatalError_LocalizedStringId('\0',0xc9,-1);
          CUnitAI__Unk_00423990(param_2);
        }
        (**(code **)(*(int *)*arg2 + 0x50))((int *)*arg2,arg3);
        uStack_68 = uStack_68 >> 1;
        uVar10 = (int)uVar10 >> 1;
        iStack_50 = arg3 + 1;
        param_1 = local_4c;
      } while (iStack_50 < param_4);
    }
    local_64 = (undefined2)arg3;
    param_1[0x2b] = (uint)arg2;
    *(undefined2 *)(param_1 + 0x2c) = local_64;
    param_1[0x51] = uVar1;
    return;
  }
  if (param_1[0x51] == 3) {
    iVar13 = 5;
  }
  else {
    if (param_1[0x51] != 4) {
      FatalError_LocalizedStringId('\0',199,-1);
      *arg8 = 0;
      return;
    }
    iVar13 = 2;
  }
                    /* WARNING: Could not recover jumptable at 0x00559545. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)(&PTR_DAT_00559b98)[iVar13])();
  return;
}
