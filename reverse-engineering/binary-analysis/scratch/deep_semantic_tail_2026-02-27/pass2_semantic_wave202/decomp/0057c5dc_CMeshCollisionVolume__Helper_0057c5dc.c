/* address: 0x0057c5dc */
/* name: CMeshCollisionVolume__Helper_0057c5dc */
/* signature: int __thiscall CMeshCollisionVolume__Helper_0057c5dc(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CMeshCollisionVolume__Helper_0057c5dc(void *this,void *param_1,int param_2)

{
  undefined4 uVar1;
  void *pvVar2;
  int *piVar3;
  int iVar4;
  void *extraout_EAX;
  uint uVar5;
  undefined *local_27c [2];
  undefined *local_274;
  undefined1 local_1f8 [64];
  undefined1 local_1b8 [24];
  undefined1 *local_1a0;
  undefined4 local_19c;
  undefined4 local_198;
  undefined4 local_194;
  undefined4 local_190;
  undefined8 local_188;
  undefined1 local_38 [8];
  undefined1 *local_30;
  code *local_2c;
  code *local_28;
  void *local_24;
  void *local_20;
  uint local_1c;
  void *local_18;
  int local_14;
  uint local_10;
  uint local_c;
  void *local_8;

  local_14 = 0;
  local_8 = (void *)0x0;
  local_24 = param_1;
  local_20 = (void *)0x0;
  local_30 = &LAB_0057c55a;
  local_2c = CMeshCollisionVolume__Helper_0057c57d;
  local_28 = CMeshCollisionVolume__Helper_0057c5b2;
  local_18 = this;
  piVar3 = CMeshCollisionVolume__Helper_00574270(*(int *)this);
  local_1c = (uint)piVar3[2] >> 3;
  CTexture__ResetDecodeContextWithDefaults(local_1b8,0x3e,0x180);
  CFastVB__ParserContext_Init(local_27c);
  local_27c[0] = &DAT_0057aea4;
  local_274 = &DAT_0057af07;
  iVar4 = __setjmp3(local_1f8,0);
  if (iVar4 == 0) {
    local_190 = 2;
    CTexture__InitializeJpegCompressionDefaults(local_1b8);
    pvVar2 = local_18;
    local_188 = _DAT_005e96b8;
    local_19c = *(undefined4 *)((int)local_18 + 0x10);
    local_198 = *(undefined4 *)((int)local_18 + 0xc);
    local_1a0 = local_38;
    local_194 = 3;
    CTexture__ResetDecodePipelineForNextChunk(local_1b8,1);
    OID__AllocObject_DefaultTag_00662b2c(*(int *)((int)pvVar2 + 0xc) * 3);
    local_8 = extraout_EAX;
    if (extraout_EAX == (void *)0x0) {
      local_14 = -0x7ff8fff2;
    }
    else {
      local_10 = *(int *)((int)pvVar2 + 0x1c) * *(int *)((int)pvVar2 + 0x30) +
                 *(int *)((int)pvVar2 + 0x18) * local_1c + *(int *)((int)pvVar2 + 4);
      uVar5 = *(int *)((int)pvVar2 + 0x10) * *(int *)((int)pvVar2 + 0x30) + local_10;
      for (; local_10 < uVar5; local_10 = local_10 + *(int *)((int)pvVar2 + 0x30)) {
        local_c = 0;
        if (*(int *)((int)pvVar2 + 0xc) != 0) {
          iVar4 = 0;
          do {
            uVar1 = *(undefined4 *)(local_10 + local_c * 4);
            *(char *)(iVar4 + (int)local_8) = (char)((uint)uVar1 >> 0x10);
            local_c = local_c + 1;
            *(char *)(iVar4 + 1 + (int)local_8) = (char)((uint)uVar1 >> 8);
            *(char *)(iVar4 + 2 + (int)local_8) = (char)uVar1;
            iVar4 = iVar4 + 3;
          } while (local_c < *(uint *)((int)pvVar2 + 0xc));
        }
        CTexture__ReadDecodeInputBytes(local_1b8,(int)&local_8,1);
      }
      CTexture__ProcessDecodeStateMachineStep(local_1b8);
      CFastVB__ReleaseOwnedObjectAndReset((int)local_1b8);
    }
  }
  else {
    local_14 = -0x7fffbffb;
  }
  OID__FreeObject_Callback(local_8);
  OID__FreeObject_Callback(local_20);
  return local_14;
}
