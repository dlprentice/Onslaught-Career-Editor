/* address: 0x0058ecdb */
/* name: CTexture__Helper_0058ecdb */
/* signature: int __fastcall CTexture__Helper_0058ecdb(void * param_1) */


int __fastcall CTexture__Helper_0058ecdb(void *param_1)

{
  int iVar1;
  void *extraout_EAX;
  undefined4 *extraout_EAX_00;
  uint uVar2;
  void *unaff_EBX;
  void *pvVar3;
  int unaff_EDI;
  int iVar4;
  undefined4 *puVar5;
  undefined1 local_24 [16];
  void *local_14;
  undefined4 *local_10;
  void *local_c;
  undefined4 *local_8;

  iVar4 = 0;
  CTexture__InitOwnedNodeList(local_24,(void *)0x464e4946,unaff_EDI);
  iVar1 = *(int *)((int)param_1 + 0x78);
  local_14 = (void *)0x0;
  local_8 = (undefined4 *)0x0;
  iVar1 = *(int *)(iVar1 + 0x60) + *(int *)(iVar1 + 0x5c) + *(int *)(iVar1 + 0x58);
  if (iVar1 != 0) {
    OID__AllocObject_DefaultTag_00662b2c(iVar1 * 4);
    local_14 = extraout_EAX;
    if (extraout_EAX == (void *)0x0) {
      iVar4 = -0x7ff8fff2;
    }
    else {
      CDXTexture__CollectHashBucketsToArray
                (*(void **)((int)param_1 + 0x78),(int)extraout_EAX,(int)unaff_EBX);
      iVar1 = *(int *)(*(int *)((int)param_1 + 0x78) + 0x60);
      CDXTexture__CollectHashBucketsToArray
                ((void *)(*(int *)((int)param_1 + 0x78) + 0x1c),(int)((int)extraout_EAX + iVar1 * 4)
                 ,(int)unaff_EBX);
      iVar1 = iVar1 + *(int *)(*(int *)((int)param_1 + 0x78) + 0x58);
      CDXTexture__CollectHashBucketsToArray
                ((void *)(*(int *)((int)param_1 + 0x78) + 0x38),(int)((int)extraout_EAX + iVar1 * 4)
                 ,(int)unaff_EBX);
      pvVar3 = (void *)(iVar1 + *(int *)(*(int *)((int)param_1 + 0x78) + 0x5c));
      CDXEngine__Helper_0055e7ae(extraout_EAX,pvVar3,4,&LAB_0058ec2f);
      local_10 = (undefined4 *)((int)pvVar3 * 0x14);
      OID__AllocObject_DefaultTag_00662b2c((int)local_10);
      local_8 = extraout_EAX_00;
      if (extraout_EAX_00 == (undefined4 *)0x0) {
        iVar4 = -0x7ff8fff2;
      }
      else {
        iVar4 = CDXTexture__RegisterSerializedChunk();
        if (-1 < iVar4) {
          puVar5 = local_8;
          for (uVar2 = (uint)local_10 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
            *puVar5 = 0;
            puVar5 = puVar5 + 1;
          }
          for (uVar2 = (uint)local_10 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
            *(undefined1 *)puVar5 = 0;
            puVar5 = (undefined4 *)((int)puVar5 + 1);
          }
          iVar4 = CDXTexture__RegisterSerializedChunk();
          if (-1 < iVar4) {
            local_c = (void *)0x0;
            if (pvVar3 != (void *)0x0) {
              local_10 = local_8;
              do {
                iVar4 = CDXTexture__ProcessTextureChunkAndEmitBindings();
                if (iVar4 < 0) goto LAB_0058eedb;
                local_c = (void *)((int)local_c + 1);
                local_10 = local_10 + 5;
              } while (local_c < pvVar3);
            }
            iVar4 = CDXTexture__RegisterSerializedChunk();
            if (-1 < iVar4) {
              pvVar3 = (void *)CTexture__Helper_00599161((int)local_24);
              if (pvVar3 < (void *)0x8001) {
                iVar4 = CTexture__EnsurePendingConstantCapacity(param_1,(int)pvVar3,(int)unaff_EBX);
                if (-1 < iVar4) {
                  CRT__MemMoveOverlapSafe
                            ((void *)(*(int *)((int)param_1 + 0x58) + 4 + (int)pvVar3 * 4),
                             (void *)(*(int *)((int)param_1 + 0x58) + 4),
                             *(int *)((int)param_1 + 0x5c) * 4 - 4);
                  iVar4 = CTexture__Helper_0059916d
                                    (local_24,(void *)(*(int *)((int)param_1 + 0x58) + 4),pvVar3,
                                     unaff_EBX);
                  if (-1 < iVar4) {
                    *(int *)((int)param_1 + 0x5c) = *(int *)((int)param_1 + 0x5c) + (int)pvVar3;
                    *(int *)((int)param_1 + 0x68) = *(int *)((int)param_1 + 0x68) + (int)pvVar3;
                    *(undefined4 *)((int)param_1 + 100) = *(undefined4 *)((int)param_1 + 0x5c);
                    iVar4 = 0;
                  }
                }
              }
              else {
                CTexture__AppendDiagnosticMessage
                          (*(void **)param_1,(int)param_1 + 0x10,0x7ef,0x5ecd98);
                iVar4 = -0x7fffbffb;
              }
            }
          }
        }
      }
    }
  }
LAB_0058eedb:
  OID__FreeObject_Callback(local_14);
  OID__FreeObject_Callback(local_8);
  CTexture__FreeOwnedNodeListAndPayloads((int)local_24);
  return iVar4;
}
