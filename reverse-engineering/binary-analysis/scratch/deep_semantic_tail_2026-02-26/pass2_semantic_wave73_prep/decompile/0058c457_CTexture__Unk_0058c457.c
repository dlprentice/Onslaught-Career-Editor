/* address: 0x0058c457 */
/* name: CTexture__Unk_0058c457 */
/* signature: int __thiscall CTexture__Unk_0058c457(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Unk_0058c457(void *this,void *param_1,void *param_2,void *param_3)

{
  void *pvVar1;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  char *pcVar5;
  char *pcVar6;
  undefined4 *puVar7;
  int unaff_EDI;
  uint uVar8;
  undefined4 *puVar9;
  double dVar10;

  pvVar1 = this;
  if (param_1 < *(void **)((int)this + 4)) {
    pvVar1 = (void *)(int)*(char *)param_1;
    uVar2 = CTexture__Helper_0056a089(this,pvVar1,unaff_EDI);
    pcVar6 = param_1;
    if (uVar2 == 0) goto LAB_0058c476;
    do {
      pcVar5 = pcVar6;
      pcVar6 = pcVar5 + 1;
      if (*(char **)((int)this + 4) <= pcVar6) break;
      pvVar3 = (void *)(int)*pcVar6;
      uVar2 = CTexture__Helper_0056a089(pvVar1,(void *)(int)*pcVar6,unaff_EDI);
      pvVar1 = pvVar3;
    } while (uVar2 != 0);
    if (*(char **)((int)this + 4) <= pcVar6) {
      return 0;
    }
    if (*pcVar6 != '.') {
      return 0;
    }
    pcVar5 = pcVar5 + 2;
    if (pcVar5 < *(char **)((int)this + 4)) {
      do {
        pvVar3 = (void *)(int)*pcVar5;
        uVar2 = CTexture__Helper_0056a089(pvVar1,(void *)(int)*pcVar5,unaff_EDI);
        pvVar1 = pvVar3;
        if (uVar2 == 0) break;
        pcVar5 = pcVar5 + 1;
      } while (pcVar5 < *(char **)((int)this + 4));
    }
  }
  else {
LAB_0058c476:
    if ((*(char **)((int)this + 4) <= (char *)((int)param_1 + 1U)) || (*(char *)param_1 != '.')) {
      return 0;
    }
    pvVar3 = (void *)(int)*(char *)((int)param_1 + 1U);
    uVar2 = CTexture__Helper_0056a089(pvVar1,pvVar3,unaff_EDI);
    if (uVar2 == 0) {
      return 0;
    }
    for (pcVar5 = (char *)((int)param_1 + 2); pcVar5 < *(char **)((int)this + 4);
        pcVar5 = pcVar5 + 1) {
      pvVar1 = (void *)(int)*pcVar5;
      uVar2 = CTexture__Helper_0056a089(pvVar3,(void *)(int)*pcVar5,unaff_EDI);
      pvVar3 = pvVar1;
      if (uVar2 == 0) break;
    }
  }
  pcVar6 = pcVar5 + 1;
  if (pcVar6 < *(char **)((int)this + 4)) {
    pvVar1 = (void *)(int)*pcVar5;
    iVar4 = CTexture__Helper_005695af((int)pvVar1);
    if (iVar4 == 0x65) {
      pvVar3 = (void *)(int)*pcVar6;
      uVar2 = CTexture__Helper_0056a089(pvVar1,pvVar3,unaff_EDI);
      if (uVar2 != 0) {
        for (pcVar5 = pcVar5 + 2; pcVar5 < *(char **)((int)this + 4); pcVar5 = pcVar5 + 1) {
          pvVar1 = (void *)(int)*pcVar5;
          uVar2 = CTexture__Helper_0056a089(pvVar3,(void *)(int)*pcVar5,unaff_EDI);
          pvVar3 = pvVar1;
          if (uVar2 == 0) break;
        }
        goto LAB_0058c57c;
      }
    }
  }
  if (pcVar5 + 2 < *(char **)((int)this + 4)) {
    pvVar1 = (void *)(int)*pcVar5;
    iVar4 = CTexture__Helper_005695af((int)pvVar1);
    if ((iVar4 == 0x65) && (*pcVar6 == '-')) {
      pvVar3 = (void *)(int)pcVar5[2];
      uVar2 = CTexture__Helper_0056a089(pvVar1,pvVar3,unaff_EDI);
      if (uVar2 != 0) {
        for (pcVar5 = pcVar5 + 3; pcVar5 < *(char **)((int)this + 4); pcVar5 = pcVar5 + 1) {
          pvVar1 = (void *)(int)*pcVar5;
          uVar2 = CTexture__Helper_0056a089(pvVar3,(void *)(int)*pcVar5,unaff_EDI);
          pvVar3 = pvVar1;
          if (uVar2 == 0) break;
        }
      }
    }
  }
LAB_0058c57c:
  if (param_2 != (void *)0x0) {
    uVar8 = (int)pcVar5 - (int)param_1;
    CDXTexture__Helper_0055def0();
    puVar7 = param_1;
    puVar9 = (undefined4 *)&stack0xffffffec;
    for (uVar2 = uVar8 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
      *puVar9 = *puVar7;
      puVar7 = puVar7 + 1;
      puVar9 = puVar9 + 1;
    }
    for (uVar2 = uVar8 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
      *(undefined1 *)puVar9 = *(undefined1 *)puVar7;
      puVar7 = (undefined4 *)((int)puVar7 + 1);
      puVar9 = (undefined4 *)((int)puVar9 + 1);
    }
    (&stack0xffffffec)[uVar8] = 0;
    dVar10 = CConsole__Helper_0055e1c4(&stack0xffffffec);
    *(double *)param_2 = dVar10;
  }
  return (int)pcVar5 - (int)param_1;
}
