/* address: 0x005994c4 */
/* name: CDXTexture__ProcessTextureChunkAndEmitBindings */
/* signature: int CDXTexture__ProcessTextureChunkAndEmitBindings(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__ProcessTextureChunkAndEmitBindings(void)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  uint uVar4;
  uint extraout_EAX;
  void *pvVar5;
  int unaff_EDI;
  char *pcVar6;
  char *pcVar7;
  void *in_stack_00000004;
  char *in_stack_00000008;
  short *in_stack_0000000c;
  undefined2 in_stack_00000010;
  uint in_stack_00000014;
  undefined1 local_30 [4];
  uint local_2c;
  void *local_24;
  int *local_20;
  short *local_1c;
  char *local_18;
  char *local_14;
  void *local_10;
  int local_c;
  int local_8;

  iVar1 = (int)in_stack_00000008;
  in_stack_00000014 = in_stack_00000014 | 0x80000000;
  local_8 = 0;
  if (((DAT_005ecf14 != *in_stack_0000000c) && (DAT_005ecf10 != *in_stack_0000000c)) &&
     (DAT_005ecf0c != *in_stack_0000000c)) {
    iVar3 = CDXTexture__RegisterSerializedChunk();
    if (iVar3 < 0) {
      return iVar3;
    }
    local_10 = (void *)0x1;
    goto LAB_00599751;
  }
  local_1c = in_stack_0000000c + 1;
  CFastVB__SelectBestNodeTreeMatch();
  iVar3 = CFastVB__ComputeNodeSpanAndStride(*(int *)(local_8 + 0x20),&local_10,&local_24);
  if (iVar3 < 0) {
    return iVar3;
  }
  if (*(int *)(local_8 + 0x30) != 0) {
    local_c = *(int *)(local_8 + 0x30);
    in_stack_00000008 = (char *)0x0;
    local_14 = (char *)0x0;
    local_18 = (char *)0x0;
    if (local_c == 0) {
LAB_00599660:
      in_stack_00000008 = local_14;
      if ((local_14 == (char *)0x0) && (in_stack_00000008 = local_18, local_18 == (char *)0x0))
      goto LAB_00599702;
    }
    else {
      do {
        iVar3 = *(int *)(local_c + 8);
        pcVar7 = in_stack_00000008;
        if (*(int *)(iVar3 + 4) == 0x10) {
          if (*(int *)(iVar3 + 0x10) == 0) {
            pvVar5 = (void *)0x0;
          }
          else {
            pvVar5 = *(void **)(*(int *)(iVar3 + 0x10) + 0x18);
          }
          if (*(int *)(iVar3 + 0x14) == 0) {
            pcVar6 = (char *)0x0;
          }
          else {
            pcVar6 = *(char **)(*(int *)(iVar3 + 0x14) + 0x18);
          }
          if (pvVar5 == (void *)0x0) {
            iVar3 = CTexture__Helper_005695af((int)*pcVar6);
            if (iVar3 == (char)*in_stack_0000000c) {
              local_18 = pcVar6;
            }
          }
          else {
            iVar3 = CFastVB__Helper_00579b39(pvVar5,0,local_30);
            if (((-1 < iVar3) &&
                (iVar3 = CTexture__Helper_005695af((int)*pcVar6), iVar3 == (char)*in_stack_0000000c)
                ) && ((pcVar7 = pcVar6, in_stack_00000014 != local_2c &&
                      ((pcVar7 = in_stack_00000008,
                       ((local_2c ^ in_stack_00000014) & 0xffff0000) == 0 && ((short)local_2c == 0))
                      )))) {
              local_14 = pcVar6;
            }
          }
        }
        in_stack_00000008 = pcVar7;
        local_c = *(int *)(local_c + 0xc);
      } while (local_c != 0);
      local_c = 0;
      if (in_stack_00000008 == (char *)0x0) goto LAB_00599660;
    }
    pvVar5 = (void *)CTexture__Helper_005695af((int)*in_stack_00000008);
    if ((void *)(int)(char)*in_stack_0000000c == pvVar5) {
      pvVar5 = (void *)(int)in_stack_00000008[1];
      uVar4 = CTexture__Helper_0056a089((void *)(int)(char)*in_stack_0000000c,pvVar5,unaff_EDI);
      if (uVar4 != 0) {
        pcVar7 = in_stack_00000008 + 2;
        while( true ) {
          pvVar2 = (void *)(int)*pcVar7;
          uVar4 = CTexture__Helper_0056a089(pvVar5,(void *)(int)*pcVar7,unaff_EDI);
          pvVar5 = pvVar2;
          if (uVar4 == 0) break;
          pcVar7 = pcVar7 + 1;
        }
        if (*pcVar7 == '\0') {
          CSoundManager__Helper_0055e2a6(in_stack_00000008 + 1);
          if (0x1fff < extraout_EAX) {
            CTexture__Helper_0058c893((void *)(*(int *)(*local_20 + 4) + 4),0,0xb56,0x5ef328);
            return -0x7fffbffb;
          }
          *(ushort *)(iVar1 + 10) = *(ushort *)(iVar1 + 10) | (ushort)(extraout_EAX << 2) | 2;
        }
      }
    }
  }
LAB_00599702:
  if ((*(byte *)(local_8 + 0x1c) & 2) != 0) {
    *(byte *)(iVar1 + 10) = *(byte *)(iVar1 + 10) | 1;
  }
  pvVar5 = *(void **)(local_8 + 0x28);
  if (pvVar5 == (void *)0x0) {
    if (*(int *)(local_8 + 0x24) != 0) {
      pvVar5 = *(void **)(local_8 + 0x24);
      goto LAB_00599722;
    }
  }
  else {
LAB_00599722:
    iVar3 = CDXTexture__SerializeFloatGridChunk(in_stack_00000004,local_10,local_24,pvVar5);
    if (iVar3 < 0) {
      return iVar3;
    }
  }
  iVar3 = CTexture__SerializeNodeTreeToBitstream
                    ((int)in_stack_00000004,*(int *)(local_8 + 0x20),1,iVar1 + 0xc);
  if (iVar3 < 0) {
    return iVar3;
  }
LAB_00599751:
  iVar3 = CDXTexture__RegisterSerializedChunk();
  if (-1 < iVar3) {
    if (DAT_005ecf10 == *in_stack_0000000c) {
      *(undefined2 *)(iVar1 + 4) = 0;
    }
    else {
      *(ushort *)(iVar1 + 4) = (DAT_005ecf0c != *in_stack_0000000c) + 1;
    }
    *(undefined2 *)(iVar1 + 6) = in_stack_00000010;
    *(undefined2 *)(iVar1 + 8) = local_10._0_2_;
  }
  return iVar3;
}
