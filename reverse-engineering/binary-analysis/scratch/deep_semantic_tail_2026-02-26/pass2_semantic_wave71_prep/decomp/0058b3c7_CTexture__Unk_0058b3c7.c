/* address: 0x0058b3c7 */
/* name: CTexture__Unk_0058b3c7 */
/* signature: void __thiscall CTexture__Unk_0058b3c7(void * this, void * param_1, uint param_2, uint param_3) */


void __thiscall CTexture__Unk_0058b3c7(void *this,void *param_1,uint param_2,uint param_3)

{
  undefined4 *puVar1;
  uint uVar2;
  void *this_00;
  undefined4 *extraout_EAX;
  int extraout_EAX_00;
  int iVar3;
  undefined4 *puVar4;
  void *unaff_EDI;
  bool bVar5;
  char *pcVar6;
  undefined4 *local_48;
  int local_44;
  int local_40;
  uint local_8;

  puVar4 = (undefined4 *)0x0;
  if (*(int *)((int)this + 0x2c) != 0) {
    return;
  }
  local_8 = param_2;
  puVar1 = local_48;
  while (local_48 = puVar1, local_8 != 0) {
    puVar1 = *(undefined4 **)((int)this + 0x40);
    local_8 = local_8 - 1;
    if (puVar1 == (undefined4 *)0x0) {
      pcVar6 = "internal error: stack underflow";
      goto LAB_0058b732;
    }
    (&local_48)[local_8] = (undefined4 *)puVar1[2];
    *(undefined4 *)((int)this + 0x40) = puVar1[3];
    puVar1[2] = 0;
    puVar1[3] = 0;
    (**(code **)*puVar1)(1);
    puVar1 = local_48;
  }
  switch(param_1) {
  case (void *)0x0:
    CTexture__Helper_0058a713(this,puVar1[6],(void *)0x1,unaff_EDI);
    break;
  case (void *)0x1:
    CTexture__Helper_0058a981((void *)puVar1[6]);
    break;
  case (void *)0x2:
    iVar3 = 0;
    goto LAB_0058b460;
  case (void *)0x3:
    iVar3 = *(int *)(local_44 + 0x18);
LAB_0058b460:
    CTexture__Helper_00589c82(this,puVar1[6],iVar3,(int)unaff_EDI);
    break;
  case (void *)0x4:
    CTexture__HandleDirective_Include((int)this);
    break;
  case (void *)0x5:
    CTexture__HandleDirective_Error((int)this);
    break;
  case (void *)0x6:
    uVar2 = puVar1[6];
    goto LAB_0058b4b8;
  case (void *)0x7:
    uVar2 = CTexture__Helper_0058a60a((void *)puVar1[6],(void *)0x0,(void *)0x0);
    goto LAB_0058b4b8;
  case (void *)0x8:
    iVar3 = CTexture__Helper_0058a60a((void *)puVar1[6],(void *)0x0,(void *)0x0);
    uVar2 = (uint)(iVar3 == 0);
LAB_0058b4b8:
    CTexture__Helper_00589f49(this,uVar2,unaff_EDI);
    break;
  case (void *)0x9:
    CTexture__Helper_00589fa1(this,puVar1[6],(int)unaff_EDI);
    break;
  case (void *)0xa:
    CTexture__Helper_0058a014((int)this);
    break;
  case (void *)0xb:
    CTexture__Helper_0058a076((int)this);
    break;
  case (void *)0xc:
    CTexture__Helper_00589f49(this,1,unaff_EDI);
    goto LAB_0058b502;
  case (void *)0xd:
    CTexture__Helper_00589fa1(this,1,(int)unaff_EDI);
LAB_0058b502:
    CTexture__Unk_0058c3fe(*(void **)((int)this + 0x54));
    break;
  case (void *)0xe:
    CTexture__Helper_0058a9ef((int)this);
    break;
  case (void *)0xf:
  case (void *)0x10:
  case (void *)0x13:
  case (void *)0x16:
  case (void *)0x17:
  case (void *)0x1a:
  case (void *)0x1d:
  case (void *)0x22:
  case (void *)0x25:
  case (void *)0x27:
  case (void *)0x29:
  case (void *)0x2b:
    local_48 = (undefined4 *)0x0;
    puVar4 = puVar1;
    break;
  case (void *)0x11:
    local_48 = (undefined4 *)0x0;
    puVar1[4] = 2;
    uVar2 = CTexture__Helper_0058aa69(this,puVar1[6],unaff_EDI);
    goto LAB_0058b596;
  case (void *)0x12:
    local_48 = (undefined4 *)0x0;
    puVar1[4] = 2;
    uVar2 = CTexture__Helper_0058a60a((void *)puVar1[6],(void *)0x0,(void *)0x0);
    goto LAB_0058b596;
  case (void *)0x14:
    local_48 = (undefined4 *)0x0;
    uVar2 = (uint)(puVar1[6] == 0);
    goto LAB_0058b596;
  case (void *)0x15:
    puVar1[6] = -puVar1[6];
    local_48 = (undefined4 *)0x0;
    puVar4 = puVar1;
    break;
  case (void *)0x18:
    uVar2 = *(int *)(local_44 + 0x18) * puVar1[6];
    local_48 = (undefined4 *)0x0;
    goto LAB_0058b596;
  case (void *)0x19:
    local_48 = (undefined4 *)0x0;
    if (*(uint *)(local_44 + 0x18) == 0) {
      CTexture__Helper_0058c893((void *)((int)this + 4),(int)this + 0x60,0x5df,0x5ea66c);
      *(undefined4 *)((int)this + 0x2c) = 1;
      puVar4 = puVar1;
      break;
    }
    uVar2 = (uint)puVar1[6] / *(uint *)(local_44 + 0x18);
    goto LAB_0058b596;
  case (void *)0x1b:
    puVar1[6] = puVar1[6] + *(int *)(local_44 + 0x18);
    local_48 = (undefined4 *)0x0;
    puVar4 = puVar1;
    break;
  case (void *)0x1c:
    puVar1[6] = puVar1[6] - *(int *)(local_44 + 0x18);
    local_48 = (undefined4 *)0x0;
    puVar4 = puVar1;
    break;
  case (void *)0x1e:
    bVar5 = (uint)puVar1[6] < *(uint *)(local_44 + 0x18);
    goto LAB_0058b5f8;
  case (void *)0x1f:
    bVar5 = *(uint *)(local_44 + 0x18) < (uint)puVar1[6];
LAB_0058b5f8:
    uVar2 = (uint)bVar5;
    local_48 = (undefined4 *)0x0;
    goto LAB_0058b596;
  case (void *)0x20:
    bVar5 = *(uint *)(local_44 + 0x18) < (uint)puVar1[6];
    goto LAB_0058b62b;
  case (void *)0x21:
    bVar5 = (uint)puVar1[6] < *(uint *)(local_44 + 0x18);
    goto LAB_0058b62b;
  case (void *)0x23:
    bVar5 = puVar1[6] != *(int *)(local_44 + 0x18);
LAB_0058b62b:
    local_48 = (undefined4 *)0x0;
    uVar2 = 1 - bVar5;
    goto LAB_0058b596;
  case (void *)0x24:
    local_48 = (undefined4 *)0x0;
    puVar1[6] = (uint)(puVar1[6] != *(int *)(local_44 + 0x18));
    puVar4 = puVar1;
    break;
  case (void *)0x26:
    local_48 = (undefined4 *)0x0;
    if (puVar1[6] != 0) {
LAB_0058b66a:
      if (*(int *)(local_44 + 0x18) != 0) goto LAB_0058b684;
    }
    local_48 = (undefined4 *)0x0;
    uVar2 = 0;
    goto LAB_0058b596;
  case (void *)0x28:
    local_48 = (undefined4 *)0x0;
    if (puVar1[6] == 0) goto LAB_0058b66a;
LAB_0058b684:
    local_48 = (undefined4 *)0x0;
    uVar2 = 1;
    goto LAB_0058b596;
  case (void *)0x2a:
    local_48 = (undefined4 *)0x0;
    if (puVar1[6] == 0) {
      local_44 = local_40;
    }
    uVar2 = *(uint *)(local_44 + 0x18);
LAB_0058b596:
    puVar1[6] = uVar2;
    puVar4 = puVar1;
    break;
  case (void *)0x2c:
  case (void *)0x2d:
  case (void *)0x2e:
    CFastVB__Helper_00426fd0(0x30);
    if (this_00 == (void *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      CTexture__Unk_005989db(this_00,(void *)((int)this + 0x60),unaff_EDI);
      puVar4 = extraout_EAX;
    }
    CTexture__Helper_0058a6e0(this,(int)puVar4,(int)unaff_EDI);
  }
  param_1 = (void *)0x0;
  if (param_2 != 0) {
    do {
      if ((&local_48)[(int)param_1] != (undefined4 *)0x0) {
        (**(code **)*(&local_48)[(int)param_1])(1);
      }
      param_1 = (void *)((int)param_1 + 1);
    } while (param_1 < param_2);
  }
  if (*(int *)((int)this + 0x2c) == 0) {
    CFastVB__Helper_00426fd0(0x14);
    if (extraout_EAX_00 == 0) {
      iVar3 = 0;
    }
    else {
      iVar3 = CTexture__Helper_005987f4();
    }
    if (iVar3 == 0) {
      pcVar6 = "internal error: out of memory";
LAB_0058b732:
      CTexture__Helper_0058c893((void *)((int)this + 4),(int)this + 0x60,0,(int)pcVar6);
      *(undefined4 *)((int)this + 0x2c) = 1;
    }
    else {
      *(int *)((int)this + 0x40) = iVar3;
    }
  }
  else if (puVar4 != (undefined4 *)0x0) {
    (**(code **)*puVar4)(1);
  }
  return;
}
