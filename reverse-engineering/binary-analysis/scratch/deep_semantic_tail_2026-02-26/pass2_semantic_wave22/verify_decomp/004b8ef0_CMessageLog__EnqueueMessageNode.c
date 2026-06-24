/* address: 0x004b8ef0 */
/* name: CMessageLog__EnqueueMessageNode */
/* signature: void __thiscall CMessageLog__EnqueueMessageNode(void * this, int param_1, void * param_2) */


void __thiscall CMessageLog__EnqueueMessageNode(void *this,int param_1,void *param_2)

{
  CSPtrSet__AddToHead((void *)((int)this + 0x18),(void *)param_1);
  return;
}
