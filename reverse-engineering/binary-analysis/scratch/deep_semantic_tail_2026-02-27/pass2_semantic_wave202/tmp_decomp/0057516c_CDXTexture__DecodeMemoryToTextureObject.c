/* address: 0x0057516c */
/* name: CDXTexture__DecodeMemoryToTextureObject */
/* signature: int CDXTexture__DecodeMemoryToTextureObject(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__DecodeMemoryToTextureObject(void)

{
  uint uVar1;
  uint *puVar2;
  int iVar3;
  int **ppiVar4;
  int *piVar5;
  undefined4 *puVar6;
  uint uVar7;
  uint *puVar8;
  int *in_stack_00000004;
  uint in_stack_00000008;
  uint in_stack_0000000c;
  uint in_stack_00000010;
  uint in_stack_00000014;
  uint in_stack_00000018;
  uint in_stack_0000001c;
  uint in_stack_00000020;
  uint in_stack_00000024;
  int in_stack_00000028;
  char cStack0000002c;
  uint in_stack_00000030;
  uint in_stack_00000034;
  int *in_stack_00000038;
  undefined4 *in_stack_0000003c;
  int in_stack_00000040;
  undefined4 *in_stack_00000044;
  undefined4 local_4bc;
  int local_bc [7];
  int local_a0 [2];
  int local_98;
  uint local_94;
  uint local_90;
  uint local_8c;
  int local_54;
  int local_50;
  uint local_4c [15];
  int *local_10;
  int *local_c;
  int *local_8;

  piVar5 = in_stack_00000038;
  CDXTexture__InitSurfaceNodeZeroed(local_a0);
  local_8 = (int *)0x0;
  in_stack_00000038 = (int *)0x0;
  local_c = (int *)0x0;
  local_10 = (int *)0x0;
  if ((((in_stack_00000004 == (int *)0x0) || (in_stack_00000008 == 0)) || (in_stack_0000000c == 0))
     || (in_stack_00000044 == (undefined4 *)0x0)) {
    uVar7 = 0x8876086c;
    goto LAB_005758a5;
  }
  if ((piVar5 == (int *)0x0) && (in_stack_00000040 == -1)) {
    piVar5 = local_bc;
  }
  uVar7 = CDXTexture__DecodeFromMemory_WithFallbackCodecs();
  if ((int)uVar7 < 0) goto LAB_005758a5;
  if (in_stack_00000040 == -1) {
    in_stack_00000040 = piVar5[5];
  }
  in_stack_0000000c = 1;
  for (; local_54 != 0; local_54 = *(int *)(local_54 + 0x4c)) {
    in_stack_0000000c = in_stack_0000000c + 1;
  }
  in_stack_00000008 = 1;
  if (in_stack_00000040 == 5) {
    if (local_50 != 0) {
      do {
        local_50 = *(int *)(local_50 + 0x50);
        in_stack_00000008 = in_stack_00000008 + 1;
      } while (local_50 != 0);
      if (in_stack_00000008 == 6) goto LAB_0057522b;
    }
    uVar7 = 0x80004005;
    goto LAB_005758a5;
  }
LAB_0057522b:
  if ((in_stack_00000010 == 0xfffffffe) || ((int)local_94 < 0)) {
    in_stack_00000010 = local_94;
  }
  else if (((in_stack_00000010 == 0) || (in_stack_00000010 == 0xffffffff)) &&
          (in_stack_00000010 = 1, 1 < local_94)) {
    do {
      in_stack_00000010 = in_stack_00000010 << 1;
    } while (in_stack_00000010 < local_94);
  }
  if ((in_stack_00000014 == 0xfffffffe) || ((int)local_90 < 0)) {
    in_stack_00000014 = local_90;
  }
  else if (((in_stack_00000014 == 0) || (in_stack_00000014 == 0xffffffff)) &&
          (in_stack_00000014 = 1, 1 < local_90)) {
    do {
      in_stack_00000014 = in_stack_00000014 << 1;
    } while (in_stack_00000014 < local_90);
  }
  if ((in_stack_00000018 == 0xfffffffe) || ((int)local_8c < 0)) {
    in_stack_00000018 = local_8c;
  }
  else if (((in_stack_00000018 == 0) || (in_stack_00000018 == 0xffffffff)) &&
          (in_stack_00000018 = 1, 1 < local_8c)) {
    do {
      in_stack_00000018 = in_stack_00000018 << 1;
    } while (in_stack_00000018 < local_8c);
  }
  if (_cStack0000002c == -1) {
    _cStack0000002c = 0x80004;
  }
  if (in_stack_00000030 == 0xffffffff) {
    in_stack_00000030 = 5;
  }
  if (in_stack_00000040 == 5) {
    in_stack_00000030 = in_stack_00000030 | 0x70000;
  }
  if (((cStack0000002c == '\x01') || ((in_stack_00000030 & 0xff) == 2)) ||
     (local_4c[0xd] = 0, (in_stack_00000030 & 0xff) == 5)) {
    local_4c[0xd] = 1;
  }
  if (local_98 == 0) {
    puVar6 = &local_4bc;
    for (iVar3 = 0x100; iVar3 != 0; iVar3 = iVar3 + -1) {
      *puVar6 = 0xffffffff;
      puVar6 = puVar6 + 1;
    }
  }
  else {
    uVar7 = 0;
    do {
      uVar1 = *(uint *)(local_98 + uVar7 * 4);
      (&local_4bc)[uVar7] =
           -(uint)(uVar1 != (in_stack_00000034 >> 0x10 & 0xff | (in_stack_00000034 & 0xff) << 0x10 |
                            in_stack_00000034 & 0xff00ff00)) & uVar1;
      uVar7 = uVar7 + 1;
    } while (uVar7 < 0x100);
    in_stack_00000034 = 0;
    if ((in_stack_00000024 != 0x29) && (local_a0[0] == 0x29)) {
      uVar7 = 0;
      do {
        if ((&local_4bc)[uVar7] != (((uVar7 | 0xffffff00) << 8 | uVar7) << 8 | uVar7)) break;
        uVar7 = uVar7 + 1;
      } while (uVar7 < 0x100);
      if (uVar7 == 0x100) {
        local_a0[0] = 0x32;
      }
      else {
        local_4c[3] = 0xff;
        local_4c[0xc] = 0xff;
        local_4c[0] = 0;
        local_4c[1] = 0x55;
        local_4c[2] = 0xaa;
        local_4c[5] = 0;
        local_4c[6] = 0x24;
        local_4c[7] = 0x49;
        local_4c[8] = 0x6d;
        local_4c[9] = 0x92;
        local_4c[10] = 0xb6;
        local_4c[0xb] = 0xdb;
        uVar7 = 0;
        do {
          if ((&local_4bc)[uVar7] !=
              (((local_4c[uVar7 & 3] | 0xffffff00) << 8 | local_4c[(uVar7 >> 2 & 7) + 5]) << 8 |
              local_4c[(uVar7 >> 5) + 5])) break;
          uVar7 = uVar7 + 1;
        } while (uVar7 < 0x100);
        if (uVar7 == 0x100) {
          local_a0[0] = 0x1b;
        }
      }
    }
  }
  iVar3 = local_a0[0];
  if (in_stack_00000024 == 0) {
    if (in_stack_00000034 != 0) {
      puVar2 = (uint *)CMeshCollisionVolume__Helper_00574270(local_a0[0]);
      uVar7 = puVar2[1];
      if ((((uVar7 == 0) || (uVar7 == 1)) || (uVar7 == 2)) && (puVar2[4] == 0)) {
        puVar8 = local_4c + 4;
        for (iVar3 = 9; iVar3 != 0; iVar3 = iVar3 + -1) {
          *puVar8 = *puVar2;
          puVar2 = puVar2 + 1;
          puVar8 = puVar8 + 1;
        }
        local_4c[4] = 0;
        local_4c[8] = 1;
        iVar3 = CFastVB__SelectBestFormatHandler
                          ((void *)0x0,in_stack_00000020,in_stack_00000040,local_4c + 4);
        if (iVar3 == 0) {
          iVar3 = local_a0[0];
        }
      }
    }
    in_stack_00000024 = CDXTexture__MapFormatTokenToInternalCode(iVar3);
    if ((in_stack_00000028 != 3) && (in_stack_00000024 == 0x14)) {
      in_stack_00000024 = 0x16;
    }
  }
  if (in_stack_0000003c == (undefined4 *)0x0) {
LAB_005754b4:
    if (in_stack_00000024 == 0x28) {
LAB_005754da:
      in_stack_00000024 = 0x15;
    }
    else if (in_stack_00000024 == 0x29) {
      in_stack_00000024 = 0x16;
      uVar7 = 0;
      do {
        if (*(char *)((int)&local_4bc + uVar7 * 4 + 3) != -1) goto LAB_005754da;
        uVar7 = uVar7 + 1;
      } while (uVar7 < 0x100);
    }
  }
  else {
    puVar6 = &local_4bc;
    for (iVar3 = 0x100; iVar3 != 0; iVar3 = iVar3 + -1) {
      *in_stack_0000003c = *puVar6;
      puVar6 = puVar6 + 1;
      in_stack_0000003c = in_stack_0000003c + 1;
    }
    if (local_98 == 0) goto LAB_005754b4;
  }
  if ((in_stack_00000028 != 0) || (local_4c[0xe] = 1, (in_stack_00000020 & 0x200) != 0)) {
    local_4c[0xe] = 0;
  }
  uVar7 = CDXTexture__NormalizeTextureConversionParams();
  if (-1 < (int)uVar7) {
    if (in_stack_00000040 == 3) {
      uVar7 = (**(code **)(*in_stack_00000004 + 0x5c))
                        (in_stack_00000004,in_stack_00000010,in_stack_00000014,in_stack_0000001c,
                         in_stack_00000020 & 0xffe07fff,in_stack_00000024,in_stack_00000028,&local_c
                         ,0);
    }
    else if (in_stack_00000040 == 4) {
      uVar7 = (**(code **)(*in_stack_00000004 + 0x60))
                        (in_stack_00000004,in_stack_00000010,in_stack_00000014,in_stack_00000018,
                         in_stack_0000001c,in_stack_00000020 & 0xffe07fff,in_stack_00000024,
                         in_stack_00000028,&local_c,0);
    }
    else if (in_stack_00000040 == 5) {
      uVar7 = (**(code **)(*in_stack_00000004 + 100))
                        (in_stack_00000004,in_stack_00000010,in_stack_0000001c,
                         in_stack_00000020 & 0xffe07fff,in_stack_00000024,in_stack_00000028,&local_c
                         ,0);
    }
    if (-1 < (int)uVar7) {
      piVar5 = local_c;
      if (local_4c[0xe] != 0) {
        if (in_stack_00000040 == 3) {
          uVar7 = (**(code **)(*in_stack_00000004 + 0x5c))
                            (in_stack_00000004,in_stack_00000010,in_stack_00000014,in_stack_0000001c
                             ,0,in_stack_00000024,2,&local_10,0);
        }
        else if (in_stack_00000040 == 4) {
          uVar7 = (**(code **)(*in_stack_00000004 + 0x60))
                            (in_stack_00000004,in_stack_00000010,in_stack_00000014,in_stack_00000018
                             ,in_stack_0000001c,0,in_stack_00000024,2,&local_10,0);
        }
        else if (in_stack_00000040 == 5) {
          uVar7 = (**(code **)(*in_stack_00000004 + 100))
                            (in_stack_00000004,in_stack_00000010,in_stack_0000001c,0,
                             in_stack_00000024,2,&local_10,0);
        }
        piVar5 = local_10;
        if ((int)uVar7 < 0) goto LAB_00575862;
      }
      in_stack_00000024 = 0;
      if (in_stack_00000008 != 0) {
        do {
          in_stack_00000014 = 0;
          if (in_stack_0000000c != 0) {
            do {
              if (in_stack_0000001c <= in_stack_00000014) break;
              if (in_stack_00000040 == 3) {
                ppiVar4 = &stack0x00000038;
LAB_00575681:
                uVar7 = (**(code **)(*piVar5 + 0x48))(piVar5,in_stack_00000014,ppiVar4);
              }
              else {
                if (in_stack_00000040 == 4) {
                  ppiVar4 = &local_8;
                  goto LAB_00575681;
                }
                if (in_stack_00000040 == 5) {
                  uVar7 = (**(code **)(*piVar5 + 0x48))
                                    (piVar5,in_stack_00000024,in_stack_00000014,&stack0x00000038);
                }
              }
              if ((int)uVar7 < 0) goto LAB_00575862;
              if (in_stack_00000040 == 3) {
LAB_005756a3:
                uVar7 = CDXTexture__UploadDecodedBufferToSurface();
              }
              else if (in_stack_00000040 == 4) {
                uVar7 = CDXTexture__ConvertSurfaceWithActiveProfile();
              }
              else if (in_stack_00000040 == 5) goto LAB_005756a3;
              if ((int)uVar7 < 0) goto LAB_00575862;
              if (local_8 != (int *)0x0) {
                (**(code **)(*local_8 + 8))(local_8);
                local_8 = (int *)0x0;
              }
              if (in_stack_00000038 != (int *)0x0) {
                (**(code **)(*in_stack_00000038 + 8))(in_stack_00000038);
                in_stack_00000038 = (int *)0x0;
              }
              in_stack_00000014 = in_stack_00000014 + 1;
            } while (in_stack_00000014 < in_stack_0000000c);
          }
          if (local_4c[0xd] == 0) {
            for (; in_stack_00000014 < in_stack_0000001c; in_stack_00000014 = in_stack_00000014 + 1)
            {
              if (in_stack_00000040 == 3) {
                ppiVar4 = &stack0x00000038;
LAB_00575771:
                uVar7 = (**(code **)(*piVar5 + 0x48))(piVar5,in_stack_00000014,ppiVar4);
              }
              else {
                if (in_stack_00000040 == 4) {
                  ppiVar4 = &local_8;
                  goto LAB_00575771;
                }
                if (in_stack_00000040 == 5) {
                  uVar7 = (**(code **)(*piVar5 + 0x48))
                                    (piVar5,in_stack_00000024,in_stack_00000014,&stack0x00000038);
                }
              }
              if ((int)uVar7 < 0) goto LAB_00575862;
              if (in_stack_00000040 == 3) {
LAB_00575797:
                uVar7 = CDXTexture__UploadDecodedBufferToSurface();
              }
              else if (in_stack_00000040 == 4) {
                uVar7 = CDXTexture__ConvertSurfaceWithActiveProfile();
              }
              else if (in_stack_00000040 == 5) goto LAB_00575797;
              if ((int)uVar7 < 0) goto LAB_00575862;
              if (local_8 != (int *)0x0) {
                (**(code **)(*local_8 + 8))(local_8);
                local_8 = (int *)0x0;
              }
              if (in_stack_00000038 != (int *)0x0) {
                (**(code **)(*in_stack_00000038 + 8))(in_stack_00000038);
                in_stack_00000038 = (int *)0x0;
              }
            }
          }
          in_stack_00000024 = in_stack_00000024 + 1;
        } while (in_stack_00000024 < in_stack_00000008);
      }
      if ((((local_4c[0xd] == 0) || (in_stack_0000001c <= in_stack_0000000c)) ||
          (uVar7 = CDXTexture__GenerateMipChainBySurfaceCopy
                             (piVar5,(int)&local_4bc,in_stack_0000000c - 1,in_stack_00000030),
          -1 < (int)uVar7)) &&
         ((local_4c[0xe] == 0 ||
          (uVar7 = (**(code **)(*in_stack_00000004 + 0x7c))(in_stack_00000004,local_10,local_c),
          -1 < (int)uVar7)))) {
        piVar5 = local_c;
        local_c = (int *)0x0;
        *in_stack_00000044 = piVar5;
        uVar7 = 0;
      }
    }
  }
LAB_00575862:
  if (local_8 != (int *)0x0) {
    (**(code **)(*local_8 + 8))(local_8);
    local_8 = (int *)0x0;
  }
  if (in_stack_00000038 != (int *)0x0) {
    (**(code **)(*in_stack_00000038 + 8))(in_stack_00000038);
    in_stack_00000038 = (int *)0x0;
  }
  if (local_c != (int *)0x0) {
    (**(code **)(*local_c + 8))(local_c);
    local_c = (int *)0x0;
  }
  if (local_10 != (int *)0x0) {
    (**(code **)(*local_10 + 8))(local_10);
    local_10 = (int *)0x0;
  }
LAB_005758a5:
  CDXTexture__FreeSurfaceNodeTree((int)local_a0);
  return uVar7;
}
