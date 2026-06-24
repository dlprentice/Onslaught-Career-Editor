/* address: 0x0058fbc5 */
/* name: CTexture__Helper_0058fbc5 */
/* signature: void __thiscall CTexture__Helper_0058fbc5(void * this, void * param_1, uint param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CTexture__Helper_0058fbc5(void *this,void *param_1,uint param_2,uint param_3)

{
  double dVar1;
  undefined4 *puVar2;
  uint uVar3;
  int extraout_EAX;
  undefined4 *puVar4;
  int extraout_EAX_00;
  void *this_00;
  undefined4 *extraout_EAX_01;
  void *this_01;
  undefined4 *extraout_EAX_02;
  int extraout_EAX_03;
  void *this_02;
  undefined4 *extraout_EAX_04;
  int extraout_EAX_05;
  int iVar5;
  void *unaff_ESI;
  undefined4 *puVar6;
  undefined4 *puVar7;
  char *pcVar8;
  undefined4 *local_48 [16];
  uint local_8;

  if (*(int *)((int)this + 0x50) != 0) {
    return;
  }
  local_8 = param_2;
  puVar7 = local_48[1];
  puVar4 = local_48[0];
  while (local_48[0] = puVar4, local_48[1] = puVar7, local_8 != 0) {
    puVar7 = *(undefined4 **)((int)this + 0x34);
    local_8 = local_8 - 1;
    if (puVar7 == (undefined4 *)0x0) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)this + 0x10,0,0x5ea698);
      *(undefined4 *)((int)this + 0x4c) = 1;
      return;
    }
    local_48[local_8] = (undefined4 *)puVar7[2];
    *(undefined4 *)((int)this + 0x34) = puVar7[3];
    puVar7[2] = 0;
    puVar7[3] = 0;
    (**(code **)*puVar7)(1);
    puVar7 = local_48[1];
    puVar4 = local_48[0];
  }
  puVar6 = (undefined4 *)0x0;
  puVar2 = this;
  switch(param_1) {
  case (void *)0x0:
  case (void *)0x6:
    goto switchD_0058fc25_caseD_0;
  case (void *)0x1:
  case (void *)0x2:
  case (void *)0x4:
  case (void *)0x5:
  case (void *)0xa:
  case (void *)0x17:
  case (void *)0x19:
  case (void *)0x1d:
  case (void *)0x23:
  case (void *)0x29:
  case (void *)0x2a:
  case (void *)0x2f:
  case (void *)0x30:
    goto LAB_0058fce5;
  case (void *)0x3:
    puVar6 = (undefined4 *)CTexture__AppendNodeAtTail_Link0c((int)puVar7,(int)puVar4);
    local_48[0] = (undefined4 *)0x0;
    local_48[1] = (undefined4 *)0x0;
    break;
  case (void *)0x7:
    if (*(int *)((int)this + 0x74) == 0) {
      *(undefined4 *)((int)this + 0x74) = puVar4[6];
    }
    goto switchD_0058fc25_caseD_0;
  case (void *)0x8:
    goto LAB_0058fca3;
  case (void *)0x9:
    local_48[0] = (undefined4 *)0x0;
    if ((*(int *)((int)this + 0x38) < 6) || (9 < *(int *)((int)this + 0x38))) {
      pcVar8 = "instruction coissue is not supported in this shader version";
      iVar5 = 0x7eb;
      puVar6 = puVar4;
      puVar2 = puVar4;
      goto LAB_0058fea7;
    }
    puVar4[0x15] = 1;
LAB_0058fca3:
    local_48[0] = (undefined4 *)0x0;
    CTexture__Helper_0058e4b5(this,puVar4,(uint)unaff_ESI);
    puVar6 = puVar4;
    break;
  case (void *)0xb:
    iVar5 = *(int *)((int)this + 0x38);
    local_48[1] = (undefined4 *)0x0;
    if (((iVar5 < 2) || (5 < iVar5)) && ((iVar5 < 0xb || (0xe < iVar5)))) {
      pcVar8 = "instruction predication is not supported in this shader version";
      iVar5 = 0x7ec;
      puVar6 = puVar7;
      puVar2 = puVar7;
      goto LAB_0058fea7;
    }
    puVar7[0x10] = puVar4;
    puVar4 = puVar7;
    goto LAB_0058fce5;
  case (void *)0xc:
  case (void *)0xd:
  case (void *)0xe:
  case (void *)0xf:
  case (void *)0x10:
  case (void *)0x11:
  case (void *)0x12:
  case (void *)0x13:
  case (void *)0x14:
    local_48[0] = (undefined4 *)0x0;
    if (1 < param_2) {
      puVar4[0xf] = puVar7;
      local_48[1] = (undefined4 *)0x0;
    }
    local_8 = 2;
    puVar6 = puVar4;
    if (2 < param_2) {
      puVar7 = puVar4 + 0x11;
      do {
        uVar3 = local_8;
        local_8 = local_8 + 1;
        puVar2 = local_48[uVar3];
        local_48[uVar3] = (undefined4 *)0x0;
        *puVar7 = puVar2;
        puVar7 = puVar7 + 1;
      } while (local_8 < param_2);
    }
    break;
  case (void *)0x15:
  case (void *)0x16:
    local_48[0] = (undefined4 *)0x0;
    local_8 = 1;
    puVar6 = puVar4;
    if (1 < param_2) {
      puVar7 = puVar4 + 0x11;
      do {
        uVar3 = local_8;
        local_8 = local_8 + 1;
        puVar2 = local_48[uVar3];
        local_48[uVar3] = (undefined4 *)0x0;
        *puVar7 = puVar2;
        puVar7 = puVar7 + 1;
      } while (local_8 < param_2);
    }
    break;
  case (void *)0x18:
    local_48[0] = (undefined4 *)0x0;
    if (puVar4[7] == 0) {
      uVar3 = CTexture__ParseChannelMaskStrict(this,puVar7 + 4,(int)unaff_ESI);
      puVar4[8] = uVar3;
      puVar6 = puVar4;
    }
    else {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)this + 0x10,0x7e6,0x5ed218);
      *(undefined4 *)((int)this + 0x4c) = 1;
      puVar4[8] = 0xf0000;
      puVar6 = puVar4;
    }
    break;
  case (void *)0x1a:
    local_48[0] = (undefined4 *)0x0;
    if (puVar4[5] == 0) {
      puVar4[5] = 0xd000000;
      puVar6 = puVar4;
      break;
    }
    pcVar8 = "not cannot be used with other modifiers";
    iVar5 = 0x7e2;
    puVar6 = puVar4;
    goto LAB_0058fea7;
  case (void *)0x1b:
    iVar5 = puVar4[5];
    local_48[0] = (undefined4 *)0x0;
    if (iVar5 == 0) {
      puVar4[5] = 0x1000000;
      puVar6 = puVar4;
      break;
    }
    if (iVar5 == 0x2000000) {
      puVar4[5] = 0x3000000;
      puVar6 = puVar4;
      break;
    }
    if (iVar5 == 0x4000000) {
      puVar4[5] = 0x5000000;
      puVar6 = puVar4;
      break;
    }
    if (iVar5 == 0x7000000) {
      puVar4[5] = 0x8000000;
      puVar6 = puVar4;
      break;
    }
    if ((iVar5 != 0x9000000) && (iVar5 != 0xa000000)) {
      puVar6 = puVar4;
      if (iVar5 == 0xb000000) {
        puVar4[5] = 0xc000000;
      }
      break;
    }
    pcVar8 = "negate and divide modifiers cannot be combined";
    iVar5 = 0x7db;
    puVar6 = puVar4;
    goto LAB_0058fea7;
  case (void *)0x1c:
    local_48[1] = (undefined4 *)0x0;
    if (puVar4[6] == 1) {
      if ((*(int *)((int)this + 0x38) < 6) || (9 < *(int *)((int)this + 0x38))) {
        pcVar8 = "complement is not supported in this shader version";
        iVar5 = 0x7ed;
        puVar6 = puVar7;
      }
      else {
        if (puVar7[5] == 0) {
          puVar7[5] = 0x6000000;
          puVar6 = puVar7;
          break;
        }
        pcVar8 = "complement cannot be used with other modifiers";
        iVar5 = 0x7dc;
        puVar6 = puVar7;
      }
    }
    else {
      pcVar8 = "invalid complement expression";
      iVar5 = 0x7da;
      puVar6 = puVar7;
    }
    goto LAB_0058fea7;
  case (void *)0x1e:
    local_48[0] = (undefined4 *)0x0;
    if (puVar4[7] == 0) {
      uVar3 = CTexture__ParseSwizzleMask(this,puVar7 + 4,(int)unaff_ESI);
      puVar4[9] = uVar3;
      puVar6 = puVar4;
    }
    else {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)this + 0x10,0x7e6,0x5ed118);
      *(undefined4 *)((int)this + 0x4c) = 1;
      puVar4[9] = 0xe40000;
      puVar6 = puVar4;
    }
    break;
  case (void *)0x21:
    puVar7 = (undefined4 *)0x0;
    goto LAB_0058ff23;
  case (void *)0x22:
LAB_0058ff23:
    puVar6 = (undefined4 *)
             CTexture__ParseScriptTokensAndBuildNodes(this,puVar4 + 4,(int)puVar7,(int)unaff_ESI);
    goto LAB_005900cf;
  case (void *)0x24:
    puVar4[6] = puVar4[6] + puVar7[6];
    local_48[0] = (undefined4 *)0x0;
    if (puVar4[10] == 0) {
      puVar4[10] = puVar7[10];
      puVar7[10] = 0;
      puVar6 = puVar4;
      break;
    }
    puVar6 = puVar4;
    if (puVar7[10] == 0) break;
    pcVar8 = "only one address register reference allowed in a relative address expression";
    iVar5 = 0x7d9;
LAB_0058fea7:
    CTexture__AppendDiagnosticMessage(*(void **)this,(int)(puVar2 + 4),iVar5,(int)pcVar8);
    *(undefined4 *)((int)this + 0x4c) = 1;
    break;
  case (void *)0x25:
    OID__AllocObject_DefaultTag_00662b2c(0x2c);
    if (extraout_EAX == 0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4 = (undefined4 *)CTexture__Helper_0059996f();
    }
    CTexture__NormalizeParserResultOrReport(this,puVar4,(int)unaff_ESI);
LAB_0058fce5:
    local_48[0] = (undefined4 *)0x0;
    puVar6 = puVar4;
    break;
  case (void *)0x26:
    OID__AllocObject_DefaultTag_00662b2c(0x2c);
    if (extraout_EAX_00 == 0) {
LAB_005900cd:
      puVar6 = (undefined4 *)0x0;
    }
    else {
      puVar6 = (undefined4 *)CTexture__Helper_0059996f();
    }
    goto LAB_005900cf;
  case (void *)0x27:
    OID__AllocObject_DefaultTag_00662b2c(0x30);
    if (this_00 == (void *)0x0) {
      puVar6 = (undefined4 *)0x0;
    }
    else {
      CTexture__NodeType8_InitFromDescriptor(this_00,(void *)((int)this + 0x10),unaff_ESI);
      puVar6 = extraout_EAX_01;
    }
    CTexture__NormalizeParserResultOrReport(this,puVar6,(int)unaff_ESI);
    puVar6[4] = 2;
    puVar6[6] = 1;
    break;
  case (void *)0x28:
    OID__AllocObject_DefaultTag_00662b2c(0x30);
    if (this_01 == (void *)0x0) {
      puVar6 = (undefined4 *)0x0;
    }
    else {
      CTexture__NodeType8_InitFromDescriptor(this_01,(void *)((int)this + 0x10),unaff_ESI);
      puVar6 = extraout_EAX_02;
    }
    CTexture__NormalizeParserResultOrReport(this,puVar6,(int)unaff_ESI);
    puVar6[4] = 2;
    puVar6[6] = 0;
    break;
  case (void *)0x2b:
    puVar4[6] = -puVar4[6];
    local_48[0] = (undefined4 *)0x0;
    puVar6 = puVar4;
    break;
  case (void *)0x2c:
  case (void *)0x2d:
    dVar1 = (double)(int)puVar4[6];
    local_48[0] = (undefined4 *)0x0;
    puVar4[4] = 5;
    if ((int)puVar4[6] < 0) {
      dVar1 = dVar1 + _DAT_005ed0c0;
    }
    goto LAB_0059008b;
  case (void *)0x2e:
    dVar1 = (double)(int)puVar4[6];
    local_48[0] = (undefined4 *)0x0;
    puVar4[4] = 5;
    if ((int)puVar4[6] < 0) {
      dVar1 = dVar1 + _DAT_005ed0c0;
    }
    goto LAB_00590089;
  case (void *)0x31:
    dVar1 = *(double *)(puVar4 + 6);
    local_48[0] = (undefined4 *)0x0;
LAB_00590089:
    dVar1 = -dVar1;
LAB_0059008b:
    local_48[0] = (undefined4 *)0x0;
    *(double *)(puVar4 + 6) = dVar1;
    puVar6 = puVar4;
    break;
  case (void *)0x32:
  case (void *)0x33:
  case (void *)0x34:
  case (void *)0x35:
  case (void *)0x36:
  case (void *)0x37:
  case (void *)0x38:
  case (void *)0x39:
  case (void *)0x3a:
  case (void *)0x3b:
  case (void *)0x3c:
    OID__AllocObject_DefaultTag_00662b2c(0x60);
    if (extraout_EAX_03 == 0) goto LAB_005900cd;
    puVar6 = (undefined4 *)CTexture__Helper_005997e1();
    goto LAB_005900cf;
  case (void *)0x3d:
  case (void *)0x3e:
  case (void *)0x3f:
    OID__AllocObject_DefaultTag_00662b2c(0x30);
    if (this_02 == (void *)0x0) goto LAB_005900cd;
    CTexture__NodeType8_InitFromDescriptor(this_02,(void *)((int)this + 0x10),unaff_ESI);
    puVar6 = extraout_EAX_04;
LAB_005900cf:
    CTexture__NormalizeParserResultOrReport(this,puVar6,(int)unaff_ESI);
  }
switchD_0058fc25_caseD_1f:
  param_1 = (void *)0x0;
  if (param_2 != 0) {
    do {
      if (local_48[(int)param_1] != (undefined4 *)0x0) {
        (**(code **)*local_48[(int)param_1])(1);
      }
      param_1 = (void *)((int)param_1 + 1);
    } while (param_1 < param_2);
  }
  if (*(int *)((int)this + 0x50) == 0) {
    OID__AllocObject_DefaultTag_00662b2c(0x14);
    if (extraout_EAX_05 == 0) {
      iVar5 = 0;
    }
    else {
      iVar5 = CTexture__Helper_005987f4();
    }
    if (iVar5 == 0) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)this + 0x10,0,0x5ea644);
      *(undefined4 *)((int)this + 0x50) = 1;
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
    else {
      *(int *)((int)this + 0x34) = iVar5;
    }
  }
  else if (puVar6 != (undefined4 *)0x0) {
    (**(code **)*puVar6)(1);
  }
  return;
switchD_0058fc25_caseD_0:
  puVar6 = (undefined4 *)0x0;
  goto switchD_0058fc25_caseD_1f;
}
