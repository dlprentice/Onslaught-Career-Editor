/* address: 0x005007f0 */
/* name: CVBufTexture__ResizeIndexBuffer */
/* signature: undefined CVBufTexture__ResizeIndexBuffer(void) */


void __thiscall CVBufTexture__ResizeIndexBuffer(undefined4 *param_1,int param_2)

{
  void *this;
  int iVar1;
  int extraout_EAX;
  int extraout_EAX_00;
  uint uVar2;
  uint uVar3;
  int unaff_EBX;
  void *pvVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  int iVar7;
  int code;
  undefined4 *local_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d56b9;
  local_c = ExceptionList;
  local_10 = param_1;
  if (param_2 != 0) {
    pvVar4 = (void *)0x400;
    if (0x400 < param_2) {
      do {
        pvVar4 = (void *)((int)pvVar4 * 2);
      } while ((int)pvVar4 < param_2);
    }
    if (pvVar4 != (void *)0x0) {
      ExceptionList = &local_c;
      local_10 = (undefined4 *)
                 OID__AllocObject(0x24,0x2f,s_C__dev_ONSLAUGHT2_vbuftexture_cp_00633d5c,0xfb);
      local_4 = 0;
      if (local_10 == (undefined4 *)0x0) {
        this = (void *)0x0;
      }
      else {
        this = (void *)CIBuffer__Constructor();
      }
      code = 2;
      iVar7 = 0xd2;
      local_4 = 0xffffffff;
      iVar1 = CIBuffer__Unk_00488330(this,pvVar4,param_1[9],param_1[8],param_1[10],0xd2);
      FatalError_LocalizedStringId(-1 < iVar1,iVar7,code);
      *(undefined1 *)(param_1 + 0xb) = 0;
      if (0 < (int)param_1[0xc]) {
        if (param_1[0xd] != 0) {
          CVBufTexture__Helper_004885e0(this,(int)&local_10,unaff_EBX);
          if (extraout_EAX < 0) {
            FatalError_LocalizedStringId('\0',0xd2,5);
          }
          else {
            if (*(char *)(param_1 + 0xb) == '\0') {
              iVar7 = 0x3e9;
              iVar1 = 0xd2;
              CVBufTexture__Helper_004885e0((void *)param_1[0x13],(int)(param_1 + 0xf),0xd2);
              FatalError_LocalizedStringId(-1 < extraout_EAX_00,iVar1,iVar7);
              *(undefined1 *)(param_1 + 0xb) = 1;
            }
            uVar3 = param_1[0xd];
            puVar5 = (undefined4 *)param_1[0xf];
            puVar6 = local_10;
            for (uVar2 = uVar3 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
              *puVar6 = *puVar5;
              puVar5 = puVar5 + 1;
              puVar6 = puVar6 + 1;
            }
            for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
              *(undefined1 *)puVar6 = *(undefined1 *)puVar5;
              puVar5 = (undefined4 *)((int)puVar5 + 1);
              puVar6 = (undefined4 *)((int)puVar6 + 1);
            }
            if (*(char *)(param_1 + 0xb) != '\0') {
              CIBuffer__Unlock();
              param_1[0xf] = 0;
              *(undefined1 *)(param_1 + 0xb) = 0;
            }
            *(undefined1 *)(param_1 + 0xb) = 1;
            param_1[0xf] = local_10;
          }
        }
        if ((undefined4 *)param_1[0x13] != (undefined4 *)0x0) {
          (*(code *)**(undefined4 **)param_1[0x13])(1);
        }
      }
      param_1[0x13] = this;
      param_1[0xc] = pvVar4;
      ExceptionList = local_c;
      return;
    }
  }
  if (param_1[0x13] != 0) {
    ExceptionList = &local_c;
    if (*(char *)(param_1 + 0xb) != '\0') {
      ExceptionList = &local_c;
      CIBuffer__Unlock();
      param_1[0xf] = 0;
      *(undefined1 *)(param_1 + 0xb) = 0;
    }
    if ((undefined4 *)param_1[0x13] != (undefined4 *)0x0) {
      (*(code *)**(undefined4 **)param_1[0x13])(1);
    }
    param_1[0x13] = 0;
  }
  param_1[0xc] = 0;
  ExceptionList = local_c;
  return;
}
