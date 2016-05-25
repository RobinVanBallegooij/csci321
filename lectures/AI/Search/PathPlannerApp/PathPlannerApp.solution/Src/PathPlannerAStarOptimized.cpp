// PathPlannerAStarOptimized.cpp: implementation of the PathPlannerAStarOptimized class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"

#include "PathPlannerApp.h"
#include "PathPlannerAStarOptimized.h"
#include "PlannerSettingsDialog.h"

#include <iostream>
using namespace std;

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

PathPlannerAStarOptimized::PathPlannerAStarOptimized()
{
	cout << "PathPlannerAStarOptimized::PathPlannerAStarOptimized" <<endl;

	ix = iy = gx = gy = 0;
	current		= NULL;
	foundGoal	= false;
	isDone		= false;	
	diagonalPenalty = false;
	heuristicWeight = 1;

	// some prime numbers that can be used for hash table size
	// 101, 151, 199, 307, 401, 499, 599, 797, 911, 997, 1999, 4001
	// NOTE:	when you turn in your project, it should be using hash table size of 
	//			199. When writing your hash table functions, you should try table sizes
	//          of 1 and 4001. 
	createdNodesHashTableSize = 199;

	createdNodesHashTable = new PlannerNode *[createdNodesHashTableSize];
	memset(createdNodesHashTable, 0, sizeof(PlannerNode*) * createdNodesHashTableSize);
}

PathPlannerAStarOptimized::~PathPlannerAStarOptimized()
{
	cout << "PathPlannerAStarOptimized::~PathPlannerAStarOptimized" <<endl;

	CleanUp();
	
	delete createdNodesHashTable;
}



void PathPlannerAStarOptimized::PlanPath(int _ix, int _iy, int _gx, int _gy)
{
	cout << "PathPlannerAStarOptimized::PlanPath" <<endl;

	ix = _ix;
	iy = _iy;
	gx = _gx;
	gy = _gy;

	current = NULL;
	foundGoal = false;
	isDone = false;


	
	PlannerNode	*rootNode = new PlannerNode(ix, iy, NULL);

	rootNode->computeHeuristicCost(gx, gy);
	rootNode->finalCost = heuristicWeight * rootNode->heuristicCost;
	
	SmartInsert(&open, rootNode);
	HashTableInsert(rootNode);
}

void PathPlannerAStarOptimized::Run()
{

	DWORD startTime = GetTickCount();


	static int successorData[8][2] = {	{0,  -1},	// N
										{1,  -1},	// NE	
										{1,   0},	// E	
										{1,   1},	// SE
										{0,   1},	// S	
										{-1,  1},	// SW						
										{-1,  0},	// W
										{-1, -1}	// NW	
	};


	PlannerNode	*successor = NULL,
				*foundNode = NULL;


	while (!open.empty()){

		// get the next best node
		current = open.back();
		open.pop_back();


		// is it the goal?
		if (current->x == gx && current->y == gy){
			cout << "goal found" << endl;
			foundGoal = true;

			while (current != NULL){
				solution.push_back(current);
				current = current->parent;
			}

			break;
		}


		// for every possible successor
		for (int i=0; i<8; i++){

			int successorX = successorData[i][0] + current->x, 
				successorY = successorData[i][1] + current->y,
				mapData	= CPathPlannerApp::instance->collisionMapData[successorY][successorX];


			if (mapData == MAP_DATA_WALL)
				continue;


			// compute the successor's Given cost
			float successorG;

			// if diagonal move
			if (diagonalPenalty && ((i%2) == 1)){
				successorG = current->givenCost + mapData * 1.4142f;
			}else{
				successorG = current->givenCost + mapData;
			}
		
			
			// check the createdNodes list
			foundNode = HashTableFind(successorX, successorY);
			

			// skip nodes that we have already generated AND are worst.
			if (foundNode && (foundNode->givenCost <= successorG))				
				continue;


			if (foundNode){
			
				// is it in open? if so remove it!
				for(int j = 0, size = open.size(); j<size; j++){
					if( (open[j]->x == successorX) && (open[j]->y == successorY) ){
						open.erase(&open[j]);
						break;
					}
				}
												
				foundNode->parent = current;
				foundNode->givenCost = successorG;
				foundNode->finalCost = foundNode->givenCost + heuristicWeight * foundNode->heuristicCost;

				SmartInsert(&open, foundNode);
			
			}else{
			
				// set up the child 
				successor = new PlannerNode(successorX, successorY, current);
				successor->givenCost = successorG;
				successor->computeHeuristicCost(gx, gy);
				successor->finalCost = successor->givenCost + heuristicWeight * successor->heuristicCost;

				// put the successor in open
				SmartInsert(&open, successor);
				
				// every time a node is made, we will add it to the "generated list"
				// this list contains both open and closed nodes. 
				HashTableInsert(successor);
			}			
		}


		//After doing one step of the planning, see if we have run over our allowed timeslice
		if ((int)(GetTickCount() - startTime) > CPathPlannerApp::instance->timeSlice)
			return;
	}


	isDone = true;

}


bool PathPlannerAStarOptimized::IsDone()
{
	//cout << "PathPlannerAStarOptimized::isDone" <<endl;
	return isDone;
}

void PathPlannerAStarOptimized::Draw(CDC *dc)
{
	//cout << "PathPlannerAStarOptimized::Draw" <<endl;

	PlannerNode* temp;
	
	// draw all previously created nodes as blue
	for(int i=0; i<createdNodesHashTableSize; i++){
		temp = createdNodesHashTable[i];

		while (temp != NULL){
			int mapData	= 20 * CPathPlannerApp::instance->collisionMapData[temp->y][temp->x];
			dc->SetPixel(temp->x, temp->y, RGB(150 - mapData, 150 - mapData, 250 - mapData));
			temp = temp->hashTableNext;
		}
	}

	// draw open nodes as green
	for (int j=0, size = open.size(); j<size; j++){
		int mapData	= 20 * CPathPlannerApp::instance->collisionMapData[open[j]->y][open[j]->x];
		dc->SetPixel(open[j]->x, open[j]->y, RGB(150 - mapData, 250 - mapData, 150 - mapData));
	}

	// draw the path (solution)
	if (!solution.empty()){
		for(int c = 0, size = solution.size(); c<size; c++){
			int mapData	= 20 * CPathPlannerApp::instance->collisionMapData[solution[c]->y][solution[c]->x];
			dc->SetPixel(solution[c]->x, solution[c]->y, RGB(250 - mapData, 150 - mapData, 150 - mapData));
		}
	
	// draw the "current path"
	}else if (!open.empty()){
		
		PlannerNode *node = current;

		while(node != NULL){
			int mapData	= 20 * CPathPlannerApp::instance->collisionMapData[node->y][node->x];
			dc->SetPixel(node->x, node->y, RGB(250 - mapData, 150 - mapData, 150 - mapData));
			node = node->parent;
		}
	}

}


void PathPlannerAStarOptimized::Settings()
{
	cout << "PathPlannerAStarOptimized::Settings()" << endl;

	CPlannerSettingsDialog dialog(NULL);

	dialog.m_heuristicWeight		= heuristicWeight;
	dialog.m_diagonalPenalty		= diagonalPenalty;
	dialog.m_closedHashTableSize	= createdNodesHashTableSize;


	if (dialog.DoModal() == IDOK){
		heuristicWeight	= dialog.m_heuristicWeight;
		diagonalPenalty	= dialog.m_diagonalPenalty? true: false;
	}
}


void PathPlannerAStarOptimized::ShowInfo()
{
	cout << "PathPlannerAStarOptimized::ShowInfo" <<endl;

	
	float goalGiveCost = -1.0;
	if (!solution.empty())
		goalGiveCost = solution[0]->givenCost;	



	char buffer[512]; 
	memset(&buffer, 0, sizeof(buffer));

	sprintf(
		buffer, 	
		" elapsedTime: %g\n runCount: %d\n isDone: %d\n foundGoal: %d\n goalGiveCost: %g\n nodesConstructed: %d\n nodesDestructed: %d\n open.size: %d\n solution.size: %d\n heuristicWeight: %g\n createdNodesHashTableSize: %d\n",		
		(double)CPathPlannerApp::instance->elapsedTime,
		CPathPlannerApp::instance->runCount,
		isDone,
		foundGoal,
		goalGiveCost,
		PlannerNode::nodesConstructed, 
		PlannerNode::nodesDestructed, 
		open.size(), 
		solution.size(),
		heuristicWeight,
		createdNodesHashTableSize
	);

	MessageBox(CPathPlannerApp::instance->m_hWnd, buffer, "Planner Information", MB_OK);
}


void PathPlannerAStarOptimized::CleanUp(){
	cout << "PathPlannerAStarOptimized::CleanUp" <<endl;

	PlannerNode	*toDelete = NULL;
	for(int i=0; i<createdNodesHashTableSize; i++){	
		while (createdNodesHashTable[i] != NULL){
			toDelete = createdNodesHashTable[i];
			createdNodesHashTable[i] = createdNodesHashTable[i]->hashTableNext;
			delete toDelete;
		}
	}

	solution.clear();
	open.clear();

	cout << "PathPlannerAStarOptimized::CleanUp Done" <<endl;

}

// inserts so the lowest priority is in the end. if lower is better for you, just use vec_back() to get it
void PathPlannerAStarOptimized::SmartInsert(vector<PlannerNode *> *vec, PlannerNode * node){
	// binarySearch: 
	// determines the index of the search key, if it is contained in the list; otherwise, (-(insertion point) - 1). 
	// The insertion point is defined as the point at which the key would be inserted into the list: the index of the 
	// first element greater than the key, or list.size(), if all elements in the list are less than the specified key. Note that this guarantees that the return value will be >= 0 if and only if the key is found.

	int insertPosition = 0;

    int i = 0;
    for(int k = (*vec).size() - 1; i <= k;)
    {
        int l = (i + k) / 2;
        int i1 = node->compareAStar((*vec)[l]);
        
		if(i1 < 0){
            i = l + 1;
			insertPosition = -(i + 1);

		}else if(i1 > 0){
            k = l - 1;
			insertPosition = -(i + 1);
        
		}else{
            insertPosition = l;
			break;
		}
    }

	if (insertPosition < 0)
		insertPosition= -insertPosition - 1;
	
	(*vec).insert(&((*vec)[insertPosition]), node);
}


// createdNodesHashTable functions
void PathPlannerAStarOptimized::HashTableInsert(PlannerNode *node){

	int hashCode = COMPUTE_HASH_CODE(node->x, node->y);
	int index = hashCode%createdNodesHashTableSize;

	PlannerNode *temp;

	temp = createdNodesHashTable[index];
	createdNodesHashTable[index] = node;
	node->hashTableNext = temp;
}

PlannerNode* PathPlannerAStarOptimized::HashTableFind(int x, int y){

	int hashCode = COMPUTE_HASH_CODE(x, y);
	int index = hashCode%createdNodesHashTableSize;

	PlannerNode *itr = createdNodesHashTable[index];

	while(itr != NULL){
		if ((itr->x == x) && (itr->y == y) )
			return itr;

		itr = itr->hashTableNext;
	}

	return NULL;
}

PlannerNode* PathPlannerAStarOptimized::HashTableRemove(int x, int y)
{
	int hashCode = COMPUTE_HASH_CODE(x, y);
	int index = hashCode%createdNodesHashTableSize;

	PlannerNode *iterator = createdNodesHashTable[index];

	if (iterator->x == x && iterator->y == y){
		createdNodesHashTable[index] = iterator->hashTableNext;
		return iterator;
	}

	while(iterator->hashTableNext){	
		if ((iterator->hashTableNext->x == x) && (iterator->hashTableNext->y == y)){
			iterator->hashTableNext = iterator->hashTableNext->hashTableNext;
			return iterator->hashTableNext;
		}

		iterator = iterator->hashTableNext;
	}

	return NULL;
}


