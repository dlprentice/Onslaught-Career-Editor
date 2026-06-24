/* address: 0x00437fe0 */
/* name: CPhysicsScriptStatements__SetOwnedString */
/* signature: void __thiscall CPhysicsScriptStatements__SetOwnedString(void * this, int param_1, void * param_2) */


void __thiscall CPhysicsScriptStatements__SetOwnedString(void *this,int param_1,void *param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;

  if (param_1 != 0) {
    OID__FreeObject(*(void **)((int)this + 0xc));
    *(undefined4 *)((int)this + 0xc) = 0;
    iVar2 = 0;
    cVar1 = *(char *)param_1;
    while (cVar1 != '\0') {
      iVar4 = iVar2 + 1;
      iVar2 = iVar2 + 1;
      cVar1 = *(char *)(iVar4 + param_1);
    }
    iVar2 = iVar2 + 1;
    uVar3 = OID__AllocObject(iVar2,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x23c);
    *(undefined4 *)((int)this + 0xc) = uVar3;
    iVar4 = 0;
    if (0 < iVar2) {
      do {
        *(undefined1 *)(*(int *)((int)this + 0xc) + iVar4) = *(undefined1 *)(iVar4 + param_1);
        iVar4 = iVar4 + 1;
      } while (iVar4 < iVar2);
    }
  }
  return;
}
