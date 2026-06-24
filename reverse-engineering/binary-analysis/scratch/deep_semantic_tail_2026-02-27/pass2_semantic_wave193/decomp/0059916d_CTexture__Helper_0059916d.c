/* address: 0x0059916d */
/* name: CTexture__Helper_0059916d */
/* signature: int __thiscall CTexture__Helper_0059916d(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Helper_0059916d(void *this,void *param_1,void *param_2,void *param_3)

{
  undefined4 *puVar1;
  void *pvVar2;
  uint uVar3;
  uint uVar4;
  void *pvVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;

  pvVar2 = param_1;
  if (param_2 == (void *)0xffffffff) {
    pvVar5 = (void *)((*(int *)((int)this + 4) + 3U >> 2) + 2);
  }
  else {
    pvVar5 = param_2;
    if (param_2 < (void *)((*(int *)((int)this + 4) + 3U >> 2) + 2)) {
      return -0x7fffbffb;
    }
  }
  if ((void *)0x8000 < pvVar5) {
    return -0x7fffbffb;
  }
  param_1 = (void *)0x0;
  *(uint *)pvVar2 = ((int)pvVar5 - 1U & 0x7fff) << 0x10 | 0xfffe;
  *(undefined4 *)((int)pvVar2 + 4) = *(undefined4 *)this;
  param_2 = (void *)((int)pvVar2 + 8);
  for (puVar1 = *(undefined4 **)((int)this + 8); puVar1 != (undefined4 *)0x0;
      puVar1 = (undefined4 *)puVar1[4]) {
    if ((*(byte *)(puVar1 + 2) & 4) == 0) {
      uVar3 = ((int)param_1 + 3U & 0xfffffffc) - (int)param_1;
      puVar6 = param_2;
      for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
        *puVar6 = 0xabababab;
        puVar6 = puVar6 + 1;
      }
      for (uVar4 = uVar3 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
        *(undefined1 *)puVar6 = 0xab;
        puVar6 = (undefined4 *)((int)puVar6 + 1);
      }
      param_2 = (void *)((int)param_2 + uVar3);
      param_1 = (void *)((int)param_1 + uVar3);
    }
    uVar3 = puVar1[1];
    puVar6 = (undefined4 *)*puVar1;
    puVar7 = param_2;
    for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *(undefined1 *)puVar7 = *(undefined1 *)puVar6;
      puVar6 = (undefined4 *)((int)puVar6 + 1);
      puVar7 = (undefined4 *)((int)puVar7 + 1);
    }
    param_2 = (void *)((int)param_2 + puVar1[1]);
    param_1 = (void *)((int)param_1 + puVar1[1]);
  }
  uVar4 = ((int)pvVar5 * 4 + -8) - (int)param_1;
  for (uVar3 = uVar4 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
    *(undefined4 *)param_2 = 0xabababab;
    param_2 = (undefined4 *)((int)param_2 + 4);
  }
  for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined1 *)param_2 = 0xab;
    param_2 = (undefined4 *)((int)param_2 + 1);
  }
  return 0;
}
