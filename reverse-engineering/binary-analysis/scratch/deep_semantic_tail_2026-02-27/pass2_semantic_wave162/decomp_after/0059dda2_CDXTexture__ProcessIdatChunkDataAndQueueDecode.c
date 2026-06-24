/* address: 0x0059dda2 */
/* name: CDXTexture__ProcessIdatChunkDataAndQueueDecode */
/* signature: void __thiscall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * this, int param_1, void * param_2) */


void __thiscall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void *this,int param_1,void *param_2)

{
  uint *puVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  int iVar6;
  void *local_4;

  iVar3 = param_1;
  puVar1 = (uint *)(param_1 + 0xd4);
  *puVar1 = *puVar1 + 1;
  if (*(uint *)(param_1 + 0xc0) <= *puVar1) {
    local_4 = this;
    if (*(char *)(param_1 + 0x113) != '\0') {
      *puVar1 = 0;
      CDXTexture__MemsetByte(param_1,*(void **)(param_1 + 0xd8),0,*(int *)(param_1 + 200) + 1);
      do {
        *(char *)(iVar3 + 0x114) = *(char *)(iVar3 + 0x114) + '\x01';
        bVar2 = *(byte *)(iVar3 + 0x114);
        if (6 < bVar2) goto LAB_0059de6c;
        iVar6 = (uint)bVar2 * 4;
        uVar4 = ((*(int *)(iVar3 + 0xb8) - *(int *)(&DAT_005f39bc + iVar6)) + -1 +
                *(uint *)(&DAT_005f39d8 + iVar6)) / *(uint *)(&DAT_005f39d8 + iVar6);
        *(uint *)(iVar3 + 0xd0) = uVar4;
        *(uint *)(iVar3 + 0xcc) = (*(byte *)(iVar3 + 0x119) * uVar4 + 7 >> 3) + 1;
      } while (((*(byte *)(iVar3 + 0x60) & 2) == 0) &&
              (*(uint *)(iVar3 + 0xc0) =
                    ((*(int *)(iVar3 + 0xbc) - *(int *)(&DAT_005f39f4 + iVar6)) + -1 +
                    *(uint *)(&DAT_005f3a10 + iVar6)) / *(uint *)(&DAT_005f3a10 + iVar6),
              *(int *)(iVar3 + 0xd0) == 0));
      if (bVar2 < 7) {
        return;
      }
    }
LAB_0059de6c:
    if ((*(byte *)(iVar3 + 0x5c) & 0x20) == 0) {
      *(int **)(iVar3 + 0x70) = &param_1;
      *(undefined4 *)(iVar3 + 0x74) = 1;
      while( true ) {
        if (*(int *)(iVar3 + 0x68) == 0) {
          if (*(int *)(iVar3 + 0xfc) == 0) {
            do {
              CDXTexture__FinalizePngChunkAndVerifyCrc((void *)iVar3,0);
              CDXTexture__Helper_00595079((void *)iVar3,(int)&local_4,4);
              iVar6 = CDXTexture__ReadU32BigEndian(&local_4);
              *(int *)(iVar3 + 0xfc) = iVar6;
              CDXTexture__InitDecodeSeedDefault(iVar3);
              CTexture__Helper_0059cd4b((void *)iVar3,iVar3 + 0x10c,4);
              if (*(int *)(iVar3 + 0x10c) != DAT_005f3a2c) {
                CDXTexture__Helper_00592d45((void *)iVar3,0x5eea24);
              }
            } while (*(int *)(iVar3 + 0xfc) == 0);
          }
          *(uint *)(iVar3 + 0x68) = *(uint *)(iVar3 + 0xa0);
          *(int *)(iVar3 + 100) = *(int *)(iVar3 + 0x9c);
          if (*(uint *)(iVar3 + 0xfc) < *(uint *)(iVar3 + 0xa0)) {
            *(uint *)(iVar3 + 0x68) = *(uint *)(iVar3 + 0xfc);
          }
          CTexture__Helper_0059cd4b((void *)iVar3,*(int *)(iVar3 + 0x9c),*(int *)(iVar3 + 0x68));
          *(int *)(iVar3 + 0xfc) = *(int *)(iVar3 + 0xfc) - *(int *)(iVar3 + 0x68);
        }
        iVar6 = CDXTexture__InflateStream_ProcessZlibState((int *)(iVar3 + 100),1);
        if (iVar6 == 1) break;
        if (iVar6 != 0) {
          pcVar5 = *(char **)(iVar3 + 0x7c);
          if (pcVar5 == (char *)0x0) {
            pcVar5 = "Decompression Error";
          }
          CDXTexture__Helper_00592d45((void *)iVar3,(int)pcVar5);
        }
        if (*(int *)(iVar3 + 0x74) == 0) {
          CDXTexture__Helper_00592d45((void *)iVar3,0x5ee9f8);
        }
      }
      if (((*(int *)(iVar3 + 0x74) == 0) || (*(int *)(iVar3 + 0x68) != 0)) ||
         (*(int *)(iVar3 + 0xfc) != 0)) {
        CDXTexture__Helper_00592d45((void *)iVar3,0x5ee9f8);
      }
      *(uint *)(iVar3 + 0x58) = *(uint *)(iVar3 + 0x58) | 8;
      *(uint *)(iVar3 + 0x5c) = *(uint *)(iVar3 + 0x5c) | 0x20;
      *(undefined4 *)(iVar3 + 0x74) = 0;
    }
    if ((*(int *)(iVar3 + 0xfc) != 0) || (*(int *)(iVar3 + 0x68) != 0)) {
      CDXTexture__Helper_00592d45((void *)iVar3,0x5f3e90);
    }
    CDXTexture__BeginAsyncDecodeJob(iVar3 + 100);
    *(uint *)(iVar3 + 0x58) = *(uint *)(iVar3 + 0x58) | 8;
  }
  return;
}
