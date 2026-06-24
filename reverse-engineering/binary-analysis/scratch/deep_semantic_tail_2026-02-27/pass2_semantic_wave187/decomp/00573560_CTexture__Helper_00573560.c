/* address: 0x00573560 */
/* name: CTexture__Helper_00573560 */
/* signature: void __thiscall CTexture__Helper_00573560(void * this, int param_1, void * param_2, void * param_3, void * param_4) */


void __thiscall
CTexture__Helper_00573560(void *this,int param_1,void *param_2,void *param_3,void *param_4)

{
  int *piVar1;
  void *pvVar2;
  void *extraout_EAX;
  void *pvVar3;
  int *ptr;
  void *pvVar4;
  void *unaff_EDI;

  pvVar2 = param_3;
  if (((*(int *)((int)this + 0xc) != 0) &&
      (piVar1 = *(int **)((int)this + 4), param_2 == (void *)*piVar1)) && (param_3 == piVar1)) {
    ptr = (int *)piVar1[1];
    if ((int *)piVar1[1] != DAT_009d0c44) {
      do {
        CTexture__DestroySubtreeRecursive((void *)ptr[2]);
        piVar1 = (int *)*ptr;
        OID__FreeObject_Callback(ptr);
        ptr = piVar1;
      } while (piVar1 != DAT_009d0c44);
    }
    *(int **)(*(int *)((int)this + 4) + 4) = DAT_009d0c44;
    *(undefined4 *)((int)this + 0xc) = 0;
    *(undefined4 *)*(undefined4 *)((int)this + 4) = *(undefined4 *)((int)this + 4);
    *(int *)(*(int *)((int)this + 4) + 8) = *(int *)((int)this + 4);
    *(undefined4 *)param_1 = **(undefined4 **)((int)this + 4);
    return;
  }
  do {
    if (param_2 == pvVar2) {
      *(void **)param_1 = param_2;
      return;
    }
    if (*(int **)((int)param_2 + 8) == DAT_009d0c44) {
      pvVar3 = *(void **)((int)param_2 + 4);
      pvVar4 = param_2;
      if (param_2 == *(void **)((int)pvVar3 + 8)) {
        do {
          pvVar4 = pvVar3;
          pvVar3 = *(void **)((int)pvVar4 + 4);
        } while (pvVar4 == *(void **)((int)pvVar3 + 8));
      }
      if (*(void **)((int)pvVar4 + 8) != pvVar3) goto LAB_0057360e;
    }
    else {
      CTexture__WalkNodeListUntilSentinel(*(int **)((int)param_2 + 8));
      pvVar3 = extraout_EAX;
LAB_0057360e:
      pvVar4 = pvVar3;
    }
    CTexture__EraseNodeFromTree(this,(int)&param_3,param_2,unaff_EDI);
    param_2 = pvVar4;
  } while( true );
}
